import abc
from typing import Optional

from backend.model import StoredUser


class DatabaseInterface(abc.ABC):
    @abc.abstractmethod
    async def lookup_user(self, username: str) -> Optional[StoredUser]:
        ...

    @abc.abstractmethod
    async def create_user(self, user: StoredUser) -> None:
        ...
