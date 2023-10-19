from typing import Optional

from pydantic import BaseModel
from strenum import StrEnum


class IsoLang(StrEnum):
    RU = "ru"
    EN = "en"
    HE = "he"  # hebrew


TextSourceKey = str


class TextSource(BaseModel):
    key: TextSourceKey  # key throughout the app
    mark: str  # short mark, conventionally in [brackets]
    description: str
    links: list[str]
    language: IsoLang


class CommentSource(BaseModel):
    key: str
    name: str
    links: list[str]
    language: IsoLang


class TanakhBookInfo(BaseModel):
    # for Torah: 1-based number (1 Genesis, 2 Exodus, ...), after that continues in increasing order (6 Joshua, 7 Judges, ...)
    id: int
    name: dict[TextSourceKey, str]


class ParshaInfo(BaseModel):
    id: int
    book_id: int
    chapter_verse_start: tuple[int, int]
    chapter_verse_end: tuple[int, int]
    name: dict[TextSourceKey, str]


class TanakhSectionMetadata(BaseModel):
    title: dict[TextSourceKey, str]
    subtitle: Optional[dict[TextSourceKey, str]]
    text_sources: list[TextSource]
    comment_sources: list[CommentSource]
    books: list[TanakhBookInfo]
    parshas: list[ParshaInfo]
