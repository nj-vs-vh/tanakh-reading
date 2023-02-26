import logging
from typing import Any, Literal, Optional, Type, TypeVar

import pydantic
from aiohttp import web
from bson import ObjectId
from pydantic import BaseModel, Field, ValidationError
from pydantic.error_wrappers import display_errors
from pymongo.results import InsertOneResult, UpdateResult
from typing_extensions import NotRequired, TypedDict

from backend.metadata import CommentSource, TextSource

logger = logging.getLogger(__name__)


# TypedDict types are used in parsers and on frontend for default parsha page rendering


CommentFormat = Literal["plain", "markdown", "html"]


class CommentData(TypedDict):
    id: NotRequired[str]
    anchor_phrase: Optional[str]
    comment: str
    format: CommentFormat
    is_starred_by_me: NotRequired[bool]


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


# pydantic models for DB and request data validation


T = TypeVar("T", bound=BaseModel)


class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str):
        return cls(v)


class PydanticModel(BaseModel):
    @classmethod
    def from_request_json(cls: Type[T], raw: Any) -> T:
        try:
            return cls.parse_obj(raw)
        except ValidationError as e:
            logger.exception(f"Error validating request JSON: {raw}")
            raise web.HTTPBadRequest(reason=display_errors(e.errors()))

    def to_public_json(self) -> dict[str, Any]:
        return self.dict()  # Config/Field-level excludes are respected


UNSET_DB_IT = ObjectId(b"0" * 12)


class DbSchemaModel(PydanticModel):
    db_id: PydanticObjectId = Field(default=UNSET_DB_IT, exclude=True)

    class Config:
        json_encoders = {
            PydanticObjectId: str,
        }

    def is_stored(self) -> bool:
        return self.db_id != UNSET_DB_IT

    def to_mongo_db(self) -> dict[str, Any]:
        dump = self.dict()
        if self.db_id != UNSET_DB_IT:
            dump["_id"] = self.db_id
        return dump

    @classmethod
    def from_mongo_db(cls: Type[T], raw: Any) -> T:
        try:
            raw["db_id"] = raw.pop("_id")
            return cls.parse_obj(raw)
        except (KeyError, ValidationError):
            logger.exception("Error parsing data from db")
            raise web.HTTPInternalServerError(reason="Internal server error")

    def inserted_as(self: T, insert_one_result: InsertOneResult) -> T:
        return self.copy(update={"db_id": insert_one_result.inserted_id})

    def upserted_as(self: T, update_one_result: UpdateResult) -> T:
        return self.copy(update={"db_id": update_one_result.upserted_id or UNSET_DB_IT})


# user / account models


class UserCredentials(PydanticModel):
    username: str = Field(min_length=5, max_length=64)
    password: str = Field(min_length=6, max_length=64)


class UserData(PydanticModel):
    full_name: str


class NewUser(PydanticModel):
    credentials: UserCredentials
    data: UserData


class StoredUser(DbSchemaModel):
    username: str
    data: UserData

    invited_by_username: Optional[str]

    is_editor: bool = False

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


# user action models


class StarredComment(DbSchemaModel):
    comment_id: PydanticObjectId
    starrer_username: str


class StarCommentRequest(PydanticModel):
    comment_id: PydanticObjectId


class TextCoords(PydanticModel):
    parsha: int
    chapter: int
    verse: int


class EditTextRequest(PydanticModel):
    text_coords: TextCoords
    text_source_key: str
    text: str


class EditedComment(PydanticModel):
    comment: str
    anchor_phrase: Optional[str]


class EditCommentRequest(PydanticModel):
    comment_id: PydanticObjectId
    edited_comment: EditedComment


# text and comment storage models


class StoredText(DbSchemaModel):
    text_coords: TextCoords
    text_source: str
    text: str
    language: str

    @pydantic.validator("text_source")
    def text_source_key_must_be_known(cls, text_source):
        if text_source not in TextSource.all():
            raise ValueError(f"Unexpectede text source: {text_source}")
        return text_source


class StoredComment(DbSchemaModel):
    text_coords: TextCoords
    comment_source: str
    anchor_phrase: Optional[str]
    comment: str
    format: CommentFormat
    language: str
    index: int  # index within one source's comments
    legacy_id: Optional[str] = None

    @pydantic.validator("comment_source")
    def validate_comment_source(cls, comment_source):
        if comment_source not in CommentSource.all():
            raise ValueError(f"Unexpectede comment source: {comment_source}")
        return comment_source


# search result models


class FoundMatches(PydanticModel):
    text: Optional[StoredText] = None
    comment: Optional[StoredComment] = None
    # single-chapter and single-verse parsha data ready for rendering
    parsha_data: Optional[ParshaData]

    @pydantic.root_validator(pre=True)
    def text_and_comment_mutually_exclusice(cls, values):
        if ("text" in values) ^ ("comment" in values):
            return values
        else:
            raise ValueError("Either text or comment must be present")


class SearchTextResult(PydanticModel):
    found_matches: list[FoundMatches]
    total_matched_texts: Optional[int]
    total_matched_comments: Optional[int]
