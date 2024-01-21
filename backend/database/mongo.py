import asyncio
import collections
import copy
import itertools
import json
import logging
import random
from concurrent.futures import ThreadPoolExecutor
from typing import (
    Any,
    Callable,
    Iterable,
    Literal,
    NamedTuple,
    Optional,
    TypeVar,
    Union,
)

import bson
import pymongo
from async_lru import alru_cache  # type: ignore
from pymongo import MongoClient

from backend import config
from backend.database.interface import (
    DatabaseInterface,
    SearchTextIn,
    SearchTextSorting,
)
from backend.metadata import get_comment_source_language, get_text_source_language
from backend.metadata.neviim import NEVIIM_METADATA
from backend.metadata.torah import TORAH_METADATA
from backend.model import (
    UNSET_DB_ID,
    ChapterData,
    CommentData,
    DisplayedUserComment,
    EditedComment,
    FoundMatch,
    ParshaData,
    SearchTextResult,
    SignupToken,
    StarredComment,
    StarredCommentData,
    StoredComment,
    StoredText,
    StoredUser,
    StoredUserComment,
    TextCoords,
    TextOrCommentIterRequest,
    UserData,
    VerseData,
)

logger = logging.getLogger(__name__)


T = TypeVar("T")

MongoAggregationPipeline = list[dict[str, Any]]


class CoordsTriplet(NamedTuple):
    """Verse coordinates used internally"""

    parsha: int
    chapter: int
    verse: int

    @classmethod
    def from_text_or_comment(cls, toc: Union[StoredText, StoredComment]) -> "CoordsTriplet":
        return CoordsTriplet(toc.text_coords.parsha, toc.text_coords.chapter, toc.text_coords.verse)


class MongoDatabase(DatabaseInterface):
    def __init__(self, mongo_client: MongoClient[dict], db_name: str):
        self.client = mongo_client
        self.db = self.client[db_name]

        self.users_coll = self.db["users"]
        self.signup_tokens_coll = self.db["signup-tokens"]
        self.access_tokens_coll = self.db["access-tokens"]
        self.starred_comments_coll = self.db["starred-comments"]

        # legacy parsha data
        self.parsha_data_coll = self.db["parsha-data"]
        # new granular collections
        self.texts_coll = self.db["texts"]
        self.comments_coll = self.db["comments"]

        self.user_comments_coll = self.db["user-comments"]

        self.parsha_data_cache: dict[int, ParshaData] = dict()
        self.threads = ThreadPoolExecutor(max_workers=8)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.client})"

    @classmethod
    def from_config(cls) -> "MongoDatabase":
        return MongoDatabase(mongo_client=MongoClient(config.MONGO_URL), db_name=config.MONGO_DB)

    async def _awrap(self, func: Callable[..., T], *args, **kwargs) -> T:
        def wrapped_func():
            return func(*args, **kwargs)

        return await asyncio.get_running_loop().run_in_executor(self.threads, wrapped_func)

    async def create_indices(self) -> None:
        logger.info("Creating indices in Mongo")
        await self._awrap(self.users_coll.create_index, [("username", pymongo.HASHED)])

        await self._awrap(self.signup_tokens_coll.create_index, [("token", pymongo.HASHED)])
        await self._awrap(self.signup_tokens_coll.create_index, [("creator_username", pymongo.HASHED)])

        await self._awrap(self.starred_comments_coll.create_index, [("starrer_username", pymongo.HASHED)])

        await self._awrap(self.access_tokens_coll.create_index, [("token", pymongo.HASHED)])

        text_coords_index = [
            ("text_coords.parsha", pymongo.ASCENDING),
            ("text_coords.chapter", pymongo.ASCENDING),
            ("text_coords.verse", pymongo.ASCENDING),
        ]
        await self._awrap(
            self.texts_coll.create_index,
            text_coords_index + [("text_source", pymongo.HASHED)],
        )
        await self._awrap(
            self.comments_coll.create_index,
            text_coords_index + [("comment_source", pymongo.HASHED)],
        )
        await self._awrap(
            self.user_comments_coll.create_index,
            text_coords_index + [("author_username", pymongo.HASHED)],
        )
        logger.info("Indices created")

        self._background_task = asyncio.create_task(self.create_text_indices())

    async def _rebuild_text_and_comments_collections(self):
        """One-time code, useful during test and debugging"""
        logger.info("Running migration from parsha data to texts and comments")
        self.texts_coll.drop()
        self.comments_coll.drop()
        starred_legacy_comment_ids = {doc["comment_id"] for doc in self.starred_comments_coll.find({})}
        new_id_by_legacy_id = dict[str, bson.ObjectId]()
        logger.info(f"Starred legacy comment ids: {len(starred_legacy_comment_ids)}")

        cursor = self.parsha_data_coll.find({})
        for doc in cursor:
            doc.pop("_id")
            parsha_data = doc
            logger.info(f"Migrating parsha #{parsha_data['parsha']}")
            texts, comments = parsha_data_to_texts_and_comments(parsha_data)
            logger.info(f"Got {len(texts)} texts and {len(comments)} comments")
            self.texts_coll.insert_many([t.to_mongo_db() for t in texts])
            logger.info("Inserted texts")
            comment_docs = [c.to_mongo_db() for c in comments]
            for comment_doc in comment_docs:
                comment_doc["_id"] = bson.ObjectId()
                if comment_doc["legacy_id"] in starred_legacy_comment_ids:
                    new_id_by_legacy_id[comment_doc["legacy_id"]] = comment_doc["_id"]
            self.comments_coll.insert_many(comment_docs)
            logger.info("Inserted comments")

        for old_comment_id, new_comment_id in new_id_by_legacy_id.items():
            self.starred_comments_coll.update_many(
                {"comment_id": old_comment_id},
                {"$set": {"comment_id": new_comment_id}},
            )
        logger.info("Saved new indices to starred comments collection")

    async def create_text_indices(self) -> None:
        logger.info("Creating text indices in the background")

        def blocking() -> None:
            logger.info("Changing unsupported languages to none")
            self.texts_coll.update_many(
                filter={"language": {"$not": {"$in": ["ru", "en"]}}},
                update={"$set": {"language": "none"}},
            )
            self.comments_coll.update_many(
                filter={"language": {"$not": {"$in": ["ru", "en"]}}},
                update={"$set": {"language": "none"}},
            )

            logger.info("Creating text index for texts collection")
            self.texts_coll.create_index([("text", pymongo.TEXT)])
            logger.info("Creating text index for comments collection")
            self.comments_coll.create_index([("anchor_phrase", pymongo.TEXT), ("comment", pymongo.TEXT)])
            logger.info("Text indices done")

        await self._awrap(blocking)

    # users

    async def lookup_user(self, username: str) -> Optional[StoredUser]:
        doc = await self._awrap(self.users_coll.find_one, {"username": username})
        if doc is None:
            logger.info(f"No user found with {username = }")
            return None
        else:
            logger.info(f"Found user with {username = }: {doc}")
            return StoredUser.from_mongo_db(doc)

    async def save_user(self, user: StoredUser) -> StoredUser:
        logger.info(f"Creating user {user}")
        res = await self._awrap(self.users_coll.insert_one, user.to_mongo_db())
        return user.inserted_as(res)

    # signup tokens

    async def lookup_signup_token(self, token: str) -> Optional[SignupToken]:
        doc = await self._awrap(self.signup_tokens_coll.find_one, {"token": token})
        if doc is None:
            return None
        else:
            return SignupToken.from_mongo_db(doc)

    async def save_signup_token(self, signup_token: SignupToken) -> SignupToken:
        res = await self._awrap(self.signup_tokens_coll.insert_one, signup_token.to_mongo_db())
        return signup_token.inserted_as(res)

    async def get_signup_token(self, creator_username: Optional[str]) -> Optional[SignupToken]:
        res = await self._awrap(self.signup_tokens_coll.find_one, {"creator_username": creator_username})
        if res is None:
            return None
        else:
            return SignupToken.from_mongo_db(res)

    # access tokens

    async def save_access_token(self, access_token: str, user: StoredUser) -> None:
        if not user.is_stored():
            raise RuntimeError("user must be stored first to be assigned access token")
        await self._awrap(
            self.access_tokens_coll.insert_one,
            {"token": access_token, "user_id": user.db_id},
        )

    async def delete_access_token(self, access_token: str) -> None:
        await self._awrap(self.access_tokens_coll.delete_one, {"token": access_token})

    async def authenticate_user(self, access_token: str) -> Optional[StoredUser]:
        pipeline = [
            {"$match": {"token": access_token}},
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "_id",
                    "as": "authenticated_users",
                }
            },
        ]
        results = list(await self._awrap(self.access_tokens_coll.aggregate, pipeline))
        if not results:
            return None
        result = results[0]
        looked_up_users = result.get("authenticated_users", [])
        if not looked_up_users:
            return None
        user = looked_up_users[0]
        return StoredUser.from_mongo_db(user)

    # starred comments

    async def save_starred_comment(self, starred_comment: StarredComment) -> None:
        def blocking(starred_comment: StarredComment):
            self.starred_comments_coll.update_one(
                filter=starred_comment.to_mongo_db(),
                update={"$set": starred_comment.to_mongo_db()},
                upsert=True,
            )

        await self._awrap(blocking, starred_comment)

    async def delete_starred_comment(self, starred_comment: StarredComment) -> None:
        await self._awrap(
            self.starred_comments_coll.delete_one,
            starred_comment.to_mongo_db(),
        )

    async def lookup_starred_comments(self, starrer_username: str, parsha: int) -> list[StarredComment]:
        def blocking():
            cursor = self.starred_comments_coll.aggregate(
                [
                    {"$match": {"starrer_username": starrer_username}},
                    {
                        "$lookup": {
                            "from": self.comments_coll.name,
                            "localField": "comment_id",
                            "foreignField": "_id",
                            "as": "comments",
                        }
                    },
                    #                     V  take the first element from joined list because it's and ID
                    {"$match": {"comments.0.text_coords.parsha": parsha}},
                    {"$project": {"comments": False}},
                ]
            )
            return [StarredComment.from_mongo_db(doc) for doc in cursor]

        return await self._awrap(blocking)

    async def count_starred_comments_by_parsha(self, starrer_username: str) -> dict[int, int]:
        def blocking():
            cursor = self.starred_comments_coll.aggregate(
                [
                    {"$match": {"starrer_username": starrer_username}},
                    {
                        "$lookup": {
                            "from": self.comments_coll.name,
                            "localField": "comment_id",
                            "foreignField": "_id",
                            "as": "comments",
                        }
                    },
                    {"$project": {"comment": {"$first": "$comments"}}},
                    {"$project": {"parsha": "$comment.text_coords.parsha"}},
                    {"$group": {"_id": "$parsha", "count": {"$sum": 1}}},
                ]
            )
            return {doc["_id"]: doc["count"] for doc in cursor if isinstance(doc["_id"], int)}

        return await self._awrap(blocking)

    async def count_starred_comments(self, starrer_username: str) -> int:
        return await self._awrap(self.starred_comments_coll.count_documents, {"starrer_username": starrer_username})

    async def load_random_starred_comment_data(self, starrer_username: str) -> Optional[StarredCommentData]:
        def blocking() -> Optional[StarredCommentData]:
            cursor = self.starred_comments_coll.aggregate(
                [
                    {"$match": {"starrer_username": starrer_username}},
                    {"$sample": {"size": 1}},
                    {
                        "$lookup": {
                            "from": "comments",
                            "localField": "comment_id",
                            "foreignField": "_id",
                            "as": "comment",
                        }
                    },
                ]
            )
            docs = list(cursor)
            try:
                comment_doc = docs[0]["comment"][0]
            except Exception:
                logger.info(f"No random starred comments found for {starrer_username!r} ({docs = })")
                return None
            comment = StoredComment.from_mongo_db(comment_doc)
            comment.is_starred = True
            coords = CoordsTriplet.from_text_or_comment(comment)
            parsha_data = self._lookup_single_verses_as_parsha_data(starrer_username, {coords}).get(coords)
            return StarredCommentData(comment=comment, parsha_data=parsha_data)

        return await self._awrap(blocking)

    async def lookup_starred_comments_data(
        self, starrer_username: str, parsha_indices: list[int], page: int, page_size: int
    ) -> list[StarredCommentData]:
        def blocking() -> list[StarredCommentData]:
            if parsha_indices:
                pipeline: MongoAggregationPipeline = [
                    {"$match": {"$expr": {"$in": ["$text_coords.parsha", parsha_indices]}}}
                ]
            else:
                pipeline = []

            pipeline.extend(
                [
                    self._text_sorting_pipeline_step(start_to_end=True),
                    {
                        "$lookup": {
                            "from": self.starred_comments_coll.name,
                            "as": "starred",
                            "let": {"comment_id": "$_id"},
                            "pipeline": [
                                {
                                    "$match": {
                                        "$expr": {
                                            "$and": [
                                                {"$eq": ["$starrer_username", starrer_username]},
                                                {"$eq": ["$comment_id", "$$comment_id"]},
                                            ]
                                        }
                                    }
                                }
                            ],
                        }
                    },
                    {"$match": {"$expr": {"$toBool": {"$size": "$starred"}}}},
                    {"$skip": page * page_size},
                    {"$limit": page_size},
                    {"$project": {"starred": False}},
                ]
            )

            logger.info(f"generated pipeline: {pipeline}")
            cursor = self.comments_coll.aggregate(pipeline)
            comments = [StoredComment.from_mongo_db(doc) for doc in cursor]
            for c in comments:
                c.is_starred = True
            single_verse_parsha_data_by_coords = self._lookup_single_verses_as_parsha_data(
                username=starrer_username,
                coord_triplets={CoordsTriplet.from_text_or_comment(c) for c in comments},
            )
            return [
                StarredCommentData(
                    comment=comment,
                    parsha_data=single_verse_parsha_data_by_coords.get(CoordsTriplet.from_text_or_comment(comment)),
                )
                for comment in comments
            ]

        return await self._awrap(blocking)

    def _set_is_starred(self, starrer_username: str, stored_comments: list[StoredComment]):
        """Modify StoredComment objects setting is_starred flag based on the data from starred-comments collection"""
        stored_comments_by_id = {sc.db_id: sc for sc in stored_comments if sc.is_stored()}

        logger.info(f"Setting is_starred flag on {len(stored_comments)} comments with {starrer_username = }")
        cursor = self.comments_coll.aggregate(
            [
                {"$limit": 1},
                {"$addFields": {"comment_id": list(stored_comments_by_id.keys())}},
                {"$project": {"comment_id": True}},
                {"$unwind": "$comment_id"},
                {
                    "$lookup": {
                        "from": "starred-comments",
                        "as": "starred",
                        "let": {"comment_id": "$comment_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "$expr": {
                                        "$and": [
                                            {"$eq": ["$starrer_username", starrer_username]},
                                            {"$eq": ["$comment_id", "$$comment_id"]},
                                        ]
                                    }
                                }
                            }
                        ],
                    }
                },
                {"$project": {"comment_id": True, "is_starred": {"$toBool": {"$size": "$starred"}}}},
            ]
        )
        total_starred = 0
        for doc in cursor:
            is_starred = doc["is_starred"]
            if is_starred:
                total_starred += 1
            stored_comments_by_id[doc["comment_id"]].is_starred = is_starred
        logger.info(f"Total starred comments: {total_starred}")

    def _lookup_single_verses_as_parsha_data(
        self,
        username: Optional[str],
        coord_triplets: set[CoordsTriplet],
    ) -> dict[CoordsTriplet, ParshaData]:
        """Load verse texts and comments and wrap them in a single-verse parsha data object"""

        texts_and_comments_by_coords: dict[CoordsTriplet, tuple[list[StoredText], list[StoredComment]]] = dict()
        logger.info(f"Fetching verses (single-verse parsha data objects) for {len(coord_triplets)} coords")
        subquery_let = {"p": "$coords.parsha", "c": "$coords.chapter", "v": "$coords.verse"}
        subquery_pipeline = [
            {
                "$match": {
                    "$expr": {
                        "$and": [
                            {"$eq": ["$text_coords.parsha", "$$p"]},
                            {"$eq": ["$text_coords.chapter", "$$c"]},
                            {"$eq": ["$text_coords.verse", "$$v"]},
                        ]
                    }
                }
            }
        ]

        for doc in self.texts_coll.aggregate(
            [
                # {
                #     "$documents": [
                #         {"parsha": parsha, "chapter": chapter, "verse": verse}
                #         for parsha, chapter, verse in coord_triplets
                #     ]
                # },
                # ^^^ $documents is not available in Mongo 5, so we emulate it below
                {"$limit": 1},
                {
                    "$addFields": {
                        "coords": [
                            {
                                "parsha": ct.parsha,
                                "chapter": ct.chapter,
                                "verse": ct.verse,
                            }
                            for ct in coord_triplets
                        ]
                    }
                },
                {"$project": {"coords": True}},
                {"$unwind": "$coords"},
                # now we have a stream of {"parsha": ..., "chapter": ..., "verse": ...} docs
                {
                    "$lookup": {
                        "from": "texts",
                        "as": "texts",
                        "let": subquery_let,
                        "pipeline": subquery_pipeline,
                    }
                },
                {
                    "$lookup": {
                        "from": "comments",
                        "as": "comments",
                        "let": subquery_let,
                        "pipeline": subquery_pipeline,
                    }
                },
            ]
        ):
            verse_texts = [StoredText.from_mongo_db(t) for t in doc["texts"]]
            verse_comments = [StoredComment.from_mongo_db(c) for c in doc["comments"]]
            texts_and_comments_by_coords[
                CoordsTriplet(
                    doc["coords"]["parsha"],
                    doc["coords"]["chapter"],
                    doc["coords"]["verse"],
                )
            ] = (verse_texts, verse_comments)

        if username is not None:
            self._set_is_starred(
                username,
                list(itertools.chain.from_iterable(comments for _, comments in texts_and_comments_by_coords.values())),
            )
        return {
            coords: texts_and_comments_to_parsha_data(texts, comments)
            for coords, (texts, comments) in texts_and_comments_by_coords.items()
        }

    # parsha data

    async def get_parsha_data(self, index: int) -> Optional[ParshaData]:
        def blocking(parsha: int) -> Optional[ParshaData]:
            query = {"text_coords.parsha": parsha}
            texts = [StoredText.from_mongo_db(d) for d in self.texts_coll.find(query)]
            if not texts:
                return None
            comments = [StoredComment.from_mongo_db(d) for d in self.comments_coll.find(query)]
            return texts_and_comments_to_parsha_data(texts, comments)

        cached = self.parsha_data_cache.get(index)
        if cached is not None:
            parsha_data = cached
        else:
            maybe_parsha_data = await self._awrap(blocking, index)
            if maybe_parsha_data is None:
                return None
            else:
                parsha_data = maybe_parsha_data
                self.parsha_data_cache[index] = parsha_data
        return copy.deepcopy(parsha_data)

    async def save_parsha_data(self, parsha_data: ParshaData, replace: bool) -> None:
        delete_existing = replace and (parsha_data["parsha"] in await self.get_available_parsha_indices())
        logger.info(f"Saving parsha data, {replace = }, {delete_existing = }")

        def blocking(parsha_data: ParshaData) -> None:
            if delete_existing:
                filter_ = {"text_coords.parsha": parsha_data["parsha"]}
                self.texts_coll.delete_many(filter_)
                self.comments_coll.delete_many(filter_)
            texts, comments = parsha_data_to_texts_and_comments(parsha_data)
            logger.info(f"Extracted {len(texts)} texts and {len(comments)} comments")
            if texts:
                self.texts_coll.insert_many([t.to_mongo_db() for t in texts])
            if comments:
                self.comments_coll.insert_many([c.to_mongo_db() for c in comments])

        await self._awrap(blocking, parsha_data)
        self.parsha_data_cache.pop(parsha_data["parsha"], None)
        self.get_available_parsha_indices.cache_clear()

    @alru_cache(maxsize=None)
    async def get_available_parsha_indices(self) -> list[int]:
        return await self._awrap(self.texts_coll.distinct, "text_coords.parsha")

    async def get_cached_parsha_indices(self) -> list[int]:
        return list(self.parsha_data_cache.keys())

    async def drop_parsha_cache(self) -> None:
        self.get_available_parsha_indices.cache_clear()
        self.parsha_data_cache.clear()

    async def edit_comment(self, comment_id: bson.ObjectId, edited_comment: EditedComment) -> None:
        comment_doc = await self._awrap(
            self.comments_coll.find_one_and_update,
            {"_id": comment_id},
            {"$set": edited_comment.dict()},
        )
        comment = StoredComment.from_mongo_db(comment_doc)
        self.parsha_data_cache.pop(comment.text_coords.parsha, None)

    async def edit_text(self, text_id: bson.ObjectId, text: str) -> None:
        text_doc = await self._awrap(
            self.texts_coll.find_one_and_update,
            {"_id": text_id},
            {"$set": {"text": text}},
        )
        stored_text = StoredText.from_mongo_db(text_doc)
        self.parsha_data_cache.pop(stored_text.text_coords.parsha, None)

    def _text_sorting_pipeline_step(self, start_to_end: bool) -> dict[str, Any]:
        order = pymongo.ASCENDING if start_to_end else pymongo.DESCENDING
        return {
            "$sort": {
                key: order
                for key in [
                    "text_coords.parsha",
                    "text_coords.chapter",
                    "text_coords.verse",
                ]
            }
        }

    async def search_text(
        self,
        query: str,
        language: str,
        page: int,
        page_size: int,
        sorting: SearchTextSorting,
        search_in: list[SearchTextIn],
        with_verse_parsha_data: bool,
        username: Optional[str],
    ) -> SearchTextResult:
        def blocking() -> SearchTextResult:
            logger.info(
                f"Searching texts with {query = } {page = } {page_size = } {sorting = } "
                + f"{search_in = } {with_verse_parsha_data = }"
            )
            if sorting is SearchTextSorting.BEST_TO_WORST:
                sort_step = {"$sort": {"score": {"$meta": "textScore"}}}
            else:
                sort_step = self._text_sorting_pipeline_step(start_to_end=sorting is SearchTextSorting.START_TO_END)

            match_step = {"$match": {"$text": {"$search": query, "$language": to_mongo_language(language)}}}
            count_pipeline: MongoAggregationPipeline = [match_step, {"$count": "total"}]
            search_pipeline: MongoAggregationPipeline = [
                match_step,
                sort_step,
                {"$skip": page * page_size},
                {"$limit": page_size},
            ]
            logger.info(
                f"Generated search pipeline:\n{json.dumps(search_pipeline, ensure_ascii=False)}\n"
                + f"and count pipeline:\n{json.dumps(count_pipeline, ensure_ascii=False)}"
            )
            if SearchTextIn.TEXTS in search_in:
                texts = [StoredText.from_mongo_db(doc) for doc in self.texts_coll.aggregate(search_pipeline)]
                try:
                    text_matches: Optional[int] = (self.texts_coll.aggregate(count_pipeline)).next()["total"]
                except StopIteration:
                    text_matches = 0
            else:
                texts = []
                text_matches = None

            if SearchTextIn.COMMENTS in search_in:
                comments = [StoredComment.from_mongo_db(doc) for doc in self.comments_coll.aggregate(search_pipeline)]
                if username is not None:
                    self._set_is_starred(username, comments)
                try:
                    comment_matches: Optional[int] = self.comments_coll.aggregate(count_pipeline).next()["total"]
                except StopIteration:
                    comment_matches = 0
            else:
                comments = []
                comment_matches = None

            texts_and_comments = texts + comments
            if not texts_and_comments:
                return SearchTextResult(
                    found_matches=[],
                    total_matched_comments=comment_matches,
                    total_matched_texts=text_matches,
                )

            logger.info(f"Got {len(texts)} texts and {len(comments)} comments")

            if len(search_in) > 1:  # e.g. we concatenate results of several queries and need to reorder them
                if sorting is SearchTextSorting.START_TO_END:
                    texts_and_comments.sort(key=CoordsTriplet.from_text_or_comment)
                elif sorting is SearchTextSorting.END_TO_START:
                    texts_and_comments.sort(key=CoordsTriplet.from_text_or_comment, reverse=True)
                elif sorting is SearchTextSorting.BEST_TO_WORST:
                    random.seed(f"{query}-{page}-{page_size}")  # ensuring query repeatability
                    # it's reasonable to expect that on a single page all results are more or less equal in score
                    random.shuffle(texts_and_comments)

            if with_verse_parsha_data:
                verse_parsha_data_by_coords = self._lookup_single_verses_as_parsha_data(
                    username=username,
                    coord_triplets={CoordsTriplet.from_text_or_comment(toc) for toc in texts_and_comments},
                )
            else:
                verse_parsha_data_by_coords = dict()

            found_matches = list[FoundMatch]()
            for toc in texts_and_comments:
                parsha_data = verse_parsha_data_by_coords.get(CoordsTriplet.from_text_or_comment(toc))
                if isinstance(toc, StoredText):
                    found_matches.append(FoundMatch(text=toc, parsha_data=parsha_data))
                else:
                    found_matches.append(FoundMatch(comment=toc, parsha_data=parsha_data))

            return SearchTextResult(
                found_matches=found_matches,
                total_matched_comments=comment_matches,
                total_matched_texts=text_matches,
            )

        return await self._awrap(blocking)

    def _match_entities_pipeline(
        self, request: TextOrCommentIterRequest, collection: Literal["texts", "comments"]
    ) -> MongoAggregationPipeline:
        return [
            {"$sort": {"_id": pymongo.ASCENDING}},
            {
                "$match": {
                    k: v
                    for k, v in {
                        "text_coords.parsha": request.position.parsha,
                        "text_coords.chapter": request.position.chapter,
                        "text_coords.verse": request.position.verse,
                        ("comment_source" if collection == "comments" else "text_source"): request.source,
                    }.items()
                    if v is not None
                }
            },
        ]

    def _iter_entities_pipeline(
        self, request: TextOrCommentIterRequest, collection: Literal["texts", "comments"]
    ) -> MongoAggregationPipeline:
        return [
            *self._match_entities_pipeline(request, collection),
            {"$skip": request.offset},
            {"$limit": 1},
        ]

    def _count_entities_pipeline(
        self, request: TextOrCommentIterRequest, collection: Literal["texts", "comments"]
    ) -> MongoAggregationPipeline:
        return [*self._match_entities_pipeline(request, collection), {"$count": "count"}]

    async def count_texts(self, request: TextOrCommentIterRequest) -> int:
        count_doc = list(
            await self._awrap(self.texts_coll.aggregate, self._count_entities_pipeline(request, collection="texts"))
        )
        return count_doc[0]["count"]

    async def count_comments(self, request: TextOrCommentIterRequest) -> int:
        count_doc = list(
            await self._awrap(
                self.comments_coll.aggregate, self._count_entities_pipeline(request, collection="comments")
            )
        )
        return count_doc[0]["count"]

    async def iter_texts(self, request: TextOrCommentIterRequest) -> Optional[StoredText]:
        docs = list(
            await self._awrap(self.texts_coll.aggregate, self._iter_entities_pipeline(request, collection="texts"))
        )
        if docs:
            return StoredText.from_mongo_db(docs[0])
        else:
            return None

    async def iter_comments(self, request: TextOrCommentIterRequest) -> Optional[StoredComment]:
        docs = list(
            await self._awrap(
                self.comments_coll.aggregate, self._iter_entities_pipeline(request, collection="comments")
            )
        )
        if docs:
            return StoredComment.from_mongo_db(docs[0])
        else:
            return None

    async def save_user_comment(self, comment: StoredUserComment) -> StoredUserComment:
        logger.info(f"Saving user comment {comment}")
        res = await self._awrap(
            self.user_comments_coll.insert_one,
            {k: v for k, v in comment.to_mongo_db().items() if k != "db_id"},  # this is a HACK but I'm tireddddd
        )
        return comment.inserted_as(res)

    async def delete_user_comment(self, user_comment_id: bson.ObjectId, author_username: str) -> bool:
        res = await self._awrap(
            self.user_comments_coll.delete_one,
            {
                "_id": user_comment_id,
                "author_username": author_username,
            },
        )
        return res.deleted_count > 0

    async def lookup_user_comments(self, username: str, parsha: int) -> list[DisplayedUserComment]:
        docs = await self._awrap(
            self.user_comments_coll.aggregate,
            [
                {"$match": {"author_username": username, "text_coords.parsha": parsha}},
                {"$sort": {"timestamp": pymongo.ASCENDING}},
                {
                    "$lookup": {
                        "from": "users",
                        "localField": "author_username",
                        "foreignField": "username",
                        "as": "_stored_users",
                    }
                },
                {"$set": {"_author_user": {"$first": "$_stored_users"}}},
                {"$set": {"author_user_data": "$_author_user.data"}},
                {"$project": {"_stored_users": False, "_author_user": False}},
            ],
        )
        return [DisplayedUserComment.from_mongo_db(doc) for doc in docs]


def to_mongo_language(iso: str) -> str:
    return (
        iso
        if iso
        in {  # see https://www.mongodb.com/docs/manual/reference/text-search-languages/#std-label-text-search-languages
            "danish",
            "da",
            "dutch",
            "nl",
            "english",
            "en",
            "finnish",
            "fi",
            "french",
            "fr",
            "german",
            "de",
            "hungarian",
            "hu",
            "italian",
            "it",
            "norwegian",
            "nb",
            "portuguese",
            "pt",
            "romanian",
            "ro",
            "russian",
            "ru",
            "spanish",
            "es",
            "swedish",
            "sv",
            "turkish",
            "tr",
        }
        else "none"
    )


def parsha_data_to_texts_and_comments(parsha_data: ParshaData) -> tuple[list[StoredText], list[StoredComment]]:
    stored_texts: list[StoredText] = []
    stored_comments: list[StoredComment] = []
    for chapter_data in parsha_data["chapters"]:
        for verse_data in chapter_data["verses"]:
            text_coords = TextCoords(
                parsha=parsha_data["parsha"],
                chapter=chapter_data["chapter"],
                verse=verse_data["verse"],
            )
            for text_source, text in verse_data["text"].items():
                stored_texts.append(
                    StoredText(
                        # not parsing text ids from parsha data here, because this is used only
                        # for saving new data to DB
                        text_coords=text_coords,
                        text_source=text_source,
                        text=text,
                        language=to_mongo_language(get_text_source_language(text_source)),
                        format=verse_data.get("text_formats", {}).get(text_source, "plain"),
                    )
                )
            for comment_source, comments in verse_data["comments"].items():
                for index, comment in enumerate(comments):
                    stored_comments.append(
                        StoredComment(
                            text_coords=text_coords,
                            comment_source=comment_source,
                            anchor_phrase=comment["anchor_phrase"],
                            comment=comment["comment"],
                            format=comment["format"],
                            language=to_mongo_language(get_comment_source_language(comment_source)),
                            index=index,
                            legacy_id=comment.get("id"),
                            is_starred=comment.get("is_starred_by_me"),
                        )
                    )
    return stored_texts, stored_comments


def texts_and_comments_to_parsha_data(texts: list[StoredText], comments: list[StoredComment]) -> ParshaData:
    if not texts:
        raise ValueError("No texts provided to consturct parsha data")
    parsha_values = {t.text_coords.parsha for t in texts} | {c.text_coords.parsha for c in comments}
    if len(parsha_values) > 1:
        raise ValueError("Stored texts and comments are from several parshas, can't construct parsha data")
    parsha_id = next(iter(parsha_values))
    section_metadata = next(
        iter(
            [
                section
                for section in [TORAH_METADATA, NEVIIM_METADATA]
                if any(parsha_info.id == parsha_id for parsha_info in section.parshas)
            ]
        ),
        None,
    )
    if section_metadata is None:
        raise ValueError("Failed to lookup Tanakh section metadata from book id")
    parsha_info = next(iter(p for p in section_metadata.parshas if p.id == parsha_id))
    book_id = parsha_info.book_id

    parsha_data = ParshaData(
        book=book_id,
        parsha=parsha_id,
        chapters=[],
    )

    texts = sorted(texts, key=lambda t: t.text_coords.chapter)
    for chapter, chapter_texts_iter in itertools.groupby(texts, key=lambda t: t.text_coords.chapter):
        chapter_texts = sorted(chapter_texts_iter, key=lambda t: t.text_coords.verse)
        chapter_data = ChapterData(chapter=chapter, verses=[])
        parsha_data["chapters"].append(chapter_data)
        for verse, verse_texts_iter in itertools.groupby(chapter_texts, key=lambda t: t.text_coords.verse):
            verse_texts = list(verse_texts_iter)
            verse_texts_source_keys = {vt.text_source for vt in verse_texts}
            if len(verse_texts_source_keys) != len(verse_texts):
                raise ValueError(f"Stored texts for verse {chapter}:{verse} contain duplicate keys: {verse_texts}")

            verse_comments = [c for c in comments if c.text_coords.chapter == chapter and c.text_coords.verse == verse]
            verse_comments.sort(key=lambda c: c.index)
            verse_data_by_source = collections.defaultdict[str, list[CommentData]](list)
            for vc in verse_comments:
                comment_data = CommentData(
                    id=str(vc.db_id) if vc.is_stored() else vc.legacy_id or "<unset>",
                    anchor_phrase=vc.anchor_phrase,
                    comment=vc.comment,
                    format=vc.format,
                )
                if vc.is_starred is True:
                    comment_data["is_starred_by_me"] = True
                verse_data_by_source[vc.comment_source].append(comment_data)

            verse_data = VerseData(
                verse=verse,
                text={vt.text_source: vt.text for vt in verse_texts},
                comments=verse_data_by_source,
                text_formats={vt.text_source: vt.format for vt in verse_texts},
            )
            if all(vt.db_id != UNSET_DB_ID for vt in verse_texts):
                verse_data["text_ids"] = {vt.text_source: str(vt.db_id) for vt in verse_texts}
            chapter_data["verses"].append(verse_data)

    return parsha_data
