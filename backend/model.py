import logging
from typing import Any, Literal, Optional, Type, TypedDict, TypeVar

from aiohttp import web
from pydantic import BaseModel, Field, ValidationError
from pydantic.error_wrappers import display_errors
from pymongo.results import InsertOneResult
from typing_extensions import NotRequired

logger = logging.getLogger(__name__)


class CommentData(TypedDict):
    id: NotRequired[str]
    anchor_phrase: Optional[str]
    comment: str
    format: Literal["plain", "markdown", "html"]
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


UNSET_DB_IT = "<not-set>"


class DbSchemaModel(PydanticModel):
    db_id: str = Field(UNSET_DB_IT, exclude=True)

    def is_stored(self) -> bool:
        return self.db_id != UNSET_DB_IT

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


class CommentCoords(DbSchemaModel):
    """Generic comment coordinates; book/parsha/chapter/verse values are used for faster validation"""

    comment_id: str  # comment id in static json file
    parsha: int
    chapter: int
    verse: int


class StarredComment(CommentCoords):
    starrer_username: str


class TextCoordsQuery(PydanticModel):
    """Generic text coords query for getting info about more or less specific parts of the text"""

    parsha: Optional[int] = None
    chapter: Optional[int] = None
    verse: Optional[int] = None

    def to_mongo_query(self) -> dict[str, int]:
        return self.dict(exclude_defaults=True)


class EditTextRequest(PydanticModel):
    parsha: int
    chapter: int
    verse: int
    translation_key: str
    new_text: str


class EditCommentRequest(PydanticModel):
    comment_coords: CommentCoords
    new_comment: str
    new_anchor_phrase: str
