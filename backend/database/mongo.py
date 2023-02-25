import asyncio
import collections
import copy
import itertools
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional, TypeVar, cast

import bson
import pymongo
from async_lru import alru_cache  # type: ignore
from pymongo import MongoClient

from backend import config
from backend.database.interface import DatabaseInterface
from backend.metadata import get_book_by_parsha
from backend.model import (
    ChapterData,
    CommentData,
    EditedComment,
    ParshaData,
    SignupToken,
    StarredComment,
    StoredComment,
    StoredText,
    StoredUser,
    TextCoords,
    VerseData,
)
from backend.server import edit_comment

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

    async def _awrap(self, func: Callable[..., T], *args) -> T:
        return await asyncio.get_running_loop().run_in_executor(self.threads, func, *args)

    async def create_indices(self) -> None:
        logger.info("Creating indices in Mongo")
        await self._awrap(self.users_coll.create_index, [("username", pymongo.HASHED)])
        await self._awrap(self.signup_tokens_coll.create_index, [("token", pymongo.HASHED)])
        await self._awrap(self.signup_tokens_coll.create_index, [("creator_username", pymongo.HASHED)])
        await self._awrap(self.starred_comments_coll.create_index, [("comment_id", pymongo.HASHED)])
        await self._awrap(
            self.starred_comments_coll.create_index,
            [
                ("starrer_username", pymongo.HASHED),
                ("parsha", pymongo.ASCENDING),
                ("chapter", pymongo.ASCENDING),
                ("verse", pymongo.ASCENDING),
            ],
        )
        logger.info("Indices created")


        # TEMP
        self.texts_coll.drop()
        self.comments_coll.drop()

        if await self._awrap(self.texts_coll.count_documents, {}) and await self._awrap(
            self.comments_coll.count_documents, {}
        ):
            logger.info("Both texts and comments collections are not empty, migration not required")
        else:
            logger.info("Running migration from parsha data to texts and comments")
            self.texts_coll.drop()
            self.comments_coll.drop()
            starred_legacy_comment_ids = {doc["comment_id"] for doc in self.starred_comments_coll.find({})}
            new_id_by_legacy_id = dict[str, bson.ObjectId]()
            logger.info(f"Starred legacy comment ids: {len(starred_legacy_comment_ids)}")

            cursor = self.parsha_data_coll.find({})
            for doc in cursor:
                doc.pop("_id")
                parsha_data = cast(ParshaData, doc)
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

            logger.info("Parsha data migration completed")

        logger.info("Migrating access tokens to directly reference object id of a user")
        self.access_tokens_coll.aggregate(
            [
                {"$set": {"user_id": {"$toObjectId": "$user_id"}}},
                {"$out": "access-tokens"},
            ]
        )
        logger.info("Access token migration completed")

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

    async def save_starred_comment(self, starred_comment: StarredComment) -> StarredComment:
        existing_comment_doc = await self._awrap(
            self.starred_comments_coll.find_one,
            {
                "comment_id": starred_comment.comment_id,
                "starrer_username": starred_comment.starrer_username,
            },
        )
        if existing_comment_doc is None:
            res = await self._awrap(self.starred_comments_coll.insert_one, starred_comment.to_mongo_db())
            return starred_comment.inserted_as(res)
        else:
            return StarredComment.from_mongo_db(existing_comment_doc)

    async def delete_starred_comment(self, starred_comment: StarredComment) -> None:
        await self._awrap(
            self.starred_comments_coll.delete_one,
            {"comment_id": starred_comment.comment_id, "starrer_username": starred_comment.starrer_username},
        )

    async def lookup_starred_comments(self, starrer_username: str, parsha: int) -> list[StarredComment]:
        def blocking():
            cursor = self.starred_comments_coll.find({"starrer_username": starrer_username, "parsha": parsha})
            return [StarredComment.from_mongo_db(doc) for doc in cursor]

        return await self._awrap(blocking)

    # parsha data

    async def get_parsha_data(self, index: int) -> Optional[ParshaData]:
        def blocking(parsha: int):
            query = {"text_coords.parsha": parsha}
            texts = [StoredText.from_mongo_db(d) for d in self.texts_coll.find(query)]
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
        if parsha_data["parsha"] in self.get_available_parsha_indices():
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
        await self._awrap(
            self.comments_coll.update_one,
            {"_id": comment_id},
            {"$set": edited_comment.to_public_json()},
        )
        comment_doc = await self._awrap(self.comments_coll.find_one, {"_id": comment_id})
        if comment_doc is None:
            raise ValueError(f"Comment not found: {comment_id}")
        comment = StoredComment.from_mongo_db(comment_doc)
        self.parsha_data_cache.pop(comment.text_coords.parsha, None)

    async def edit_text(self, text_coords: TextCoords, text_source_key: str, text: str) -> None:
        await self._awrap(
            self.texts_coll.update_one,
            {
                "text_coords.parsha": text_coords.parsha,
                "text_coords.chapter": text_coords.chapter,
                "text_coords.verse": text_coords.verse,
                "text_source": text_source_key,
            },
            {"$set": {"text": text}},
        )
        self.parsha_data_cache.pop(text_coords.parsha)


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
                        text_coords=text_coords,
                        text_source=text_source,
                        text=text,
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
                            index=index,
                            legacy_id=comment["id"],
                        )
                    )
    return stored_texts, stored_comments


def texts_and_comments_to_parsha_data(texts: list[StoredText], comments: list[StoredComment]) -> Optional[ParshaData]:
    if not texts:
        return None
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
                        id=str(vc.db_id) if vc.is_stored() else vc.legacy_id,
                        anchor_phrase=vc.anchor_phrase,
                        comment=vc.comment,
                        format=vc.format,
                    )
                )

            chapter_data["verses"].append(
                VerseData(
                    verse=verse,
                    text={vt.text_source: vt.text for vt in verse_texts},
                    comments=verse_data_by_source,
                )
            )

    return parsha_data
