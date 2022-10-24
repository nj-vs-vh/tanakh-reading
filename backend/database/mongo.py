import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from pymongo import MongoClient

from backend import config
from backend.database.interface import DatabaseInterface
from backend.model import StoredUser

logger = logging.getLogger(__name__)


class MongoDatabase(DatabaseInterface):
    USERS_COLLECTION = "users"

    def __init__(self, mongo_client: MongoClient[dict], db_name: str):
        self.client = mongo_client
        self.db = self.client[db_name]
        self.users_coll = self.db[self.USERS_COLLECTION]
        self.threads = ThreadPoolExecutor(max_workers=8)

    @classmethod
    def from_config(cls) -> "MongoDatabase":
        return MongoDatabase(mongo_client=MongoClient(config.MONGO_URL), db_name=config.MONGO_DB)

    async def lookup_user(self, username: str) -> Optional[StoredUser]:
        doc = await asyncio.get_running_loop().run_in_executor(
            self.threads, self.users_coll.find_one, {"username": username}
        )
        if doc is None:
            logger.info(f"No user found with {username = }")
            return None
        else:
            logger.info(f"Found user with {username = }: {doc}")
            return StoredUser.from_mongo_db(doc)

    async def create_user(self, user: StoredUser) -> None:
        logger.info(f"Creating user {user}")
        await asyncio.get_running_loop().run_in_executor(self.threads, self.users_coll.insert_one, user.dict())
