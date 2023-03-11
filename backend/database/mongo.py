import asyncio
import collections
import copy
import itertools
import json
import logging
import random
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Optional, TypeVar, Union

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
from backend.metadata import (
    comment_source_languages,
    get_book_by_parsha,
    text_source_languages,
)
from backend.model import (
    ChapterData,
    CommentData,
    EditedComment,
    FoundMatch,
    ParshaData,
    SearchTextResult,
    SignupToken,
    StarredComment,
    StoredComment,
    StoredText,
    StoredUser,
    TextCoords,
    VerseData,
)

logger = logging.getLogger(__name__)


T = TypeVar("T")


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
        await self._awrap(self.texts_coll.create_index, text_coords_index + [("text_source", pymongo.HASHED)])
        await self._awrap(self.comments_coll.create_index, text_coords_index + [("comment_source", pymongo.HASHED)])
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

    async def save_parsha_data(self, parsha_data: ParshaData) -> None:
        if parsha_data["parsha"] in await self.get_available_parsha_indices():
            raise ValueError(f"Parsha #{parsha_data['parsha']} already exists")

        def blocking(parsha_data: ParshaData) -> None:
            texts, comments = parsha_data_to_texts_and_comments(parsha_data)
            self.texts_coll.insert_many([t.to_mongo_db() for t in texts])
            self.comments_coll.insert_many([c.to_mongo_db() for c in comments])

        await self._awrap(blocking, parsha_data)
        self.parsha_data_cache.pop(parsha_data["parsha"], None)
        self.get_available_parsha_indices.cache_clear()

    @alru_cache(maxsize=None)
    async def get_available_parsha_indices(self) -> list[int]:
        return await self._awrap(self.texts_coll.distinct, "text_coords.parsha")

    async def get_cached_parsha_indices(self) -> list[int]:
        return list(self.parsha_data_cache.keys())

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

    async def search_text(
        self,
        query: str,
        language: str,
        page: int,
        page_size: int,
        sorting: SearchTextSorting,
        search_in: list[SearchTextIn],
        with_verse_parsha_data: bool,
    ) -> SearchTextResult:
        def blocking() -> SearchTextResult:
            logger.info(
                f"Searching texts with {query = } {page = } {page_size = } {sorting = } "
                + f"{search_in = } {with_verse_parsha_data = }"
            )
            if sorting is SearchTextSorting.BEST_TO_WORST:
                sort_step: dict[str, Any] = {"score": {"$meta": "textScore"}}
            else:
                if sorting is SearchTextSorting.END_TO_START:
                    order = pymongo.DESCENDING
                else:
                    order = pymongo.ASCENDING
                sort_step = {key: order for key in ["text_coords.parsha", "text_coords.chapter", "text_coords.verse"]}

            match_step = {"$match": {"$text": {"$search": query, "$language": to_mongo_language(language)}}}
            count_pipeline: list[dict[str, Any]] = [match_step, {"$count": "total"}]
            search_pipeline: list[dict[str, Any]] = [
                match_step,
                {"$sort": sort_step},
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

            def toc_to_coord_triplet(toc: Union[StoredComment, StoredText]) -> tuple[int, int, int]:
                return (toc.text_coords.parsha, toc.text_coords.chapter, toc.text_coords.verse)

            if len(search_in) > 1:  # e.g. we concatenate results of several queries and need to reorder them
                if sorting is SearchTextSorting.START_TO_END:
                    texts_and_comments.sort(key=toc_to_coord_triplet)
                elif sorting is SearchTextSorting.END_TO_START:
                    texts_and_comments.sort(key=toc_to_coord_triplet, reverse=True)
                elif sorting is SearchTextSorting.BEST_TO_WORST:
                    random.seed(f"{query}-{page}-{page_size}")  # ensuring query repeatability
                    # it's reasonable to expect that on a single page all results are more or less equal in score
                    random.shuffle(texts_and_comments)

            verse_parsha_data_by_coords: dict[tuple[int, int, int], ParshaData] = dict()
            if with_verse_parsha_data:
                coord_triplets = {toc_to_coord_triplet(toc) for toc in texts_and_comments}
                logger.info(f"Fetching verses for {len(coord_triplets)} coords")
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
                        # NOTE: ^^^ $documents is not available in Mongo 5, so we emulate it below
                        {"$limit": 1},
                        {
                            "$addFields": {
                                "coords": [
                                    {"parsha": parsha, "chapter": chapter, "verse": verse}
                                    for parsha, chapter, verse in coord_triplets
                                ]
                            }
                        },
                        {"$project": {"coords": True}},
                        {"$unwind": "$coords"},
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
                    verse_parsha_data_by_coords[
                        (doc["coords"]["parsha"], doc["coords"]["chapter"], doc["coords"]["verse"])
                    ] = texts_and_comments_to_parsha_data(verse_texts, verse_comments)

            found_matches = list[FoundMatch]()
            for toc in texts_and_comments:
                parsha_data = verse_parsha_data_by_coords.get(toc_to_coord_triplet(toc))
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
                book=parsha_data["book"],
                parsha=parsha_data["parsha"],
                chapter=chapter_data["chapter"],
                verse=verse_data["verse"],
            )
            for text_source, text in verse_data["text"].items():
                stored_texts.append(
                    StoredText(
                        # not parsing text ids from parsha data here, because this is used only for saving new data to DB
                        text_coords=text_coords,
                        text_source=text_source,
                        text=text,
                        language=to_mongo_language(text_source_languages[text_source]),
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
                            language=to_mongo_language(comment_source_languages[comment_source]),
                            index=index,
                            legacy_id=comment.get("id"),
                        )
                    )
    return stored_texts, stored_comments


def texts_and_comments_to_parsha_data(texts: list[StoredText], comments: list[StoredComment]) -> ParshaData:
    if not texts:
        raise ValueError("No texts provided to consturct parsha data")
    parsha_values = {t.text_coords.parsha for t in texts} | {c.text_coords.parsha for c in comments}
    if len(parsha_values) > 1:
        raise ValueError("Stored texts and comments are from several parshas, can't construct parsha data")
    parsha = next(iter(parsha_values))
    book = get_book_by_parsha(parsha)
    parsha_data = ParshaData(
        book=book,
        parsha=parsha,
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
                verse_data_by_source[vc.comment_source].append(
                    CommentData(
                        id=str(vc.db_id) if vc.is_stored() else vc.legacy_id or "<unset>",
                        anchor_phrase=vc.anchor_phrase,
                        comment=vc.comment,
                        format=vc.format,
                    )
                )

            chapter_data["verses"].append(
                VerseData(
                    verse=verse,
                    text={vt.text_source: vt.text for vt in verse_texts},
                    text_ids={vt.text_source: str(vt.db_id) for vt in verse_texts},
                    comments=verse_data_by_source,
                )
            )

    return parsha_data
