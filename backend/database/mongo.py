import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
import secrets
from typing import Awaitable, Callable, Optional, TypeVar

from pymongo import MongoClient

from backend import config
from backend.auth import generate_signup_token
from backend.database.interface import DatabaseInterface
from backend.model import SignupToken, StoredUser

logger = logging.getLogger(__name__)


T = TypeVar("T")


class MongoDatabase(DatabaseInterface):
    def __init__(self, mongo_client: MongoClient[dict], db_name: str):
        self.client = mongo_client
        self.db = self.client[db_name]
        self.users_coll = self.db["users"]
        self.signup_tokens_coll = self.db["signup-tokens"]
        self.threads = ThreadPoolExecutor(max_workers=8)

    @classmethod
    def from_config(cls) -> "MongoDatabase":
        return MongoDatabase(mongo_client=MongoClient(config.MONGO_URL), db_name=config.MONGO_DB)

    async def _awrap(self, func: Callable[..., T], *args) -> T:
        return await asyncio.get_running_loop().run_in_executor(self.threads, func, *args)

    async def get_root_signup_token(self) -> SignupToken:
        root_token_doc = await self._awrap(self.signup_tokens_coll.find_one, {"creator_username": None})
        if root_token_doc is None:
            logger.info("Creating root signup token")
            new_root_token = SignupToken(creator_username=None, token=generate_signup_token())
            return await self.save_signup_token(new_root_token)
        else:
            return SignupToken.from_mongo_db(root_token_doc)

    async def lookup_signup_token(self, token: str) -> Optional[SignupToken]:
        doc = await self._awrap(self.signup_tokens_coll.find_one, {"token": token})
        if doc is None:
            return None
        else:
            return SignupToken.from_mongo_db(doc)

    async def save_signup_token(self, signup_token: SignupToken) -> SignupToken:
        res = await self._awrap(self.signup_tokens_coll.insert_one, signup_token.to_mongo_db())
        return signup_token.inserted_as(res)

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
        res = await self._awrap(self.users_coll.insert_one, user.dict())
        return user.inserted_as(res)
