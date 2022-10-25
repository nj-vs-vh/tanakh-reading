import logging
from typing import Any, Literal, Optional, Type, TypedDict, TypeVar

from aiohttp import web
from pydantic import BaseModel, Field, ValidationError
from pydantic.error_wrappers import display_errors
from pymongo.results import InsertOneResult

logger = logging.getLogger(__name__)


class CommentData(TypedDict):
    anchor_phrase: Optional[str]
    comment: str
    format: Literal["plain", "markdown", "html"]


class VerseData(TypedDict):
    verse: int
    text: dict[str, str]
    comments: dict[str, list[CommentData]]


class ChapterData(TypedDict):
    chapter: int
    verses: list[VerseData]


class ParshaData(TypedDict):
    book: int
    parsha: int
    chapters: list[ChapterData]


T = TypeVar("T", bound=BaseModel)


class PydanticModel(BaseModel):
    @classmethod
    def from_request_json(cls: Type[T], raw: Any) -> T:
        try:
            return cls.parse_obj(raw)
        except ValidationError as e:
            raise web.HTTPBadRequest(reason=display_errors(e.errors()))

    def to_public_json(self) -> dict[str, Any]:
        return self.dict()  # Config/Field-level excludes are respected


class DbSchemaModel(PydanticModel):
    db_id: str = Field("n/a", exclude=True)

    def is_stored(self) -> bool:
        return self.db_id != "n/a"

    def to_mongo_db(self) -> dict[str, Any]:
        return self.dict()  # Config/Field-level excludes are respected

    @classmethod
    def from_mongo_db(cls: Type[T], raw: Any) -> T:
        try:
            raw["db_id"] = str(raw.pop("_id"))  # id field returned by MongoDB
            return cls.parse_obj(raw)
        except (KeyError, ValidationError):
            logger.exception("Error parsing data from db")
            raise web.HTTPInternalServerError(reason="Internal server error")

    def inserted_as(self: T, insert_one_result: InsertOneResult) -> T:
        return self.copy(update={"db_id": str(insert_one_result.inserted_id)})


class SubmittedUserCredentials(PydanticModel):
    class Config:
        min_anystr_length = 3
        max_anystr_length = 128

    username: str
    password: str


class SubmittedUserData(SubmittedUserCredentials):
    full_name: str


class StoredUser(DbSchemaModel):
    username: str
    full_name: str

    invited_by_username: Optional[str]

    password_hash: str
    salt: str

    def to_public_json(self) -> dict[str, Any]:
        dump = super().to_public_json()
        dump.pop("password_hash")
        dump.pop("salt")
        return dump


class SignupToken(DbSchemaModel):
    creator_username: Optional[str]
    token: str
