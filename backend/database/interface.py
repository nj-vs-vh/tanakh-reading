import abc
import logging
from enum import Enum
from typing import Optional

from bson import ObjectId

from backend.auth import generate_signup_token
from backend.model import (
    EditedComment,
    ParshaData,
    SearchTextResult,
    SignupToken,
    StarredComment,
    StarredCommentData,
    StoredComment,
    StoredText,
    StoredUser,
    TextOrCommentIterRequest,
)

logger = logging.getLogger(__name__)


class SearchTextSorting(Enum):
    BEST_TO_WORST = "best_to_worst"
    START_TO_END = "start_to_end"
    END_TO_START = "end_to_start"


class SearchTextIn(Enum):
    TEXTS = "texts"
    COMMENTS = "comments"


class DatabaseInterface(abc.ABC):
    async def setup(self) -> None:
        logger.info("Reading root signup token")
        root_signup_token = await self.get_root_signup_token()
        if root_signup_token is None:
            root_signup_token = await self.save_signup_token(
                SignupToken(creator_username=None, token=generate_signup_token())
            )
        logger.info(f"Root signup token: {root_signup_token}")
        await self.create_indices()

    @abc.abstractmethod
    async def create_indices(self) -> None:
        """Must be indempotent as it is run on every app startup"""
        ...

    # user management

    @abc.abstractmethod
    async def lookup_user(self, username: str) -> Optional[StoredUser]:
        ...

    @abc.abstractmethod
    async def save_user(self, user: StoredUser) -> StoredUser:
        ...

    # signup token management

    async def get_root_signup_token(self) -> Optional[SignupToken]:
        return await self.get_signup_token(creator_username=None)

    @abc.abstractmethod
    async def lookup_signup_token(self, token: str) -> Optional[SignupToken]:
        ...

    @abc.abstractmethod
    async def get_signup_token(self, creator_username: Optional[str]) -> Optional[SignupToken]:
        ...

    @abc.abstractmethod
    async def save_signup_token(self, signup_token: SignupToken) -> SignupToken:
        ...

    # access token management

    @abc.abstractmethod
    async def save_access_token(self, access_token: str, user: StoredUser) -> None:
        ...

    @abc.abstractmethod
    async def delete_access_token(self, access_token: str) -> None:
        ...

    @abc.abstractmethod
    async def authenticate_user(self, access_token: str) -> Optional[StoredUser]:
        ...

    # starred comments

    @abc.abstractmethod
    async def save_starred_comment(self, starred_comment: StarredComment) -> None:
        ...

    @abc.abstractmethod
    async def delete_starred_comment(self, starred_comment: StarredComment) -> None:
        ...

    @abc.abstractmethod
    async def lookup_starred_comments(self, starrer_username: str, parsha: int) -> list[StarredComment]:
        ...

    @abc.abstractmethod
    async def count_starred_comments(self, starrer_username: str) -> int:
        ...

    @abc.abstractmethod
    async def load_random_starred_comment_data(self, starrer_username: str) -> Optional[StarredCommentData]:
        pass

    @abc.abstractmethod
    async def lookup_starred_comments_data(
        self, starrer_username: str, parsha_indices: list[int], page: int, page_size: int
    ) -> list[StarredCommentData]:
        ...

    @abc.abstractmethod
    async def count_starred_comments_by_parsha(self, starrer_username: str) -> dict[int, int]:
        ...

    # parsha data storage

    @abc.abstractmethod
    async def get_parsha_data(self, index: int) -> Optional[ParshaData]:
        ...

    @abc.abstractmethod
    async def drop_parsha_cache(self) -> None:
        ...

    @abc.abstractmethod
    async def save_parsha_data(self, parsha_data: ParshaData) -> None:
        ...

    @abc.abstractmethod
    async def get_available_parsha_indices(self) -> list[int]:
        ...

    @abc.abstractmethod
    async def get_cached_parsha_indices(self) -> list[int]:
        ...

    @abc.abstractmethod
    async def edit_comment(self, comment_id: ObjectId, edited_comment: EditedComment) -> None:
        ...

    @abc.abstractmethod
    async def edit_text(self, text_id: ObjectId, text: str) -> None:
        ...

    # full text search

    @abc.abstractmethod
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
        """Each returned ParshaData will have only one chapter with one verse, containing the matched phrase"""
        ...

    @abc.abstractmethod
    async def count_texts(self, request: TextOrCommentIterRequest) -> int:
        ...

    @abc.abstractmethod
    async def count_comments(self, request: TextOrCommentIterRequest) -> int:
        ...

    @abc.abstractmethod
    async def iter_texts(self, request: TextOrCommentIterRequest) -> Optional[StoredText]:
        ...

    @abc.abstractmethod
    async def iter_comments(self, request: TextOrCommentIterRequest) -> Optional[StoredComment]:
        ...
