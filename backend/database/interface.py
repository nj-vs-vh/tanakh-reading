import abc
import logging
from typing import Optional

from backend.model import SignupToken, StoredUser

logger = logging.getLogger(__name__)


class DatabaseInterface(abc.ABC):
    async def setup(self) -> None:
        logger.info(f"Root signup token: {await self.get_root_signup_token()}")

    @abc.abstractmethod
    async def lookup_user(self, username: str) -> Optional[StoredUser]:
        ...

    @abc.abstractmethod
    async def save_user(self, user: StoredUser) -> StoredUser:
        ...

    @abc.abstractmethod
    async def get_root_signup_token(self) -> SignupToken:
        ...

    @abc.abstractmethod
    async def lookup_signup_token(self, token: str) -> Optional[SignupToken]:
        ...

    @abc.abstractmethod
    async def save_signup_token(self, signup_token: SignupToken) -> SignupToken:
        ...
