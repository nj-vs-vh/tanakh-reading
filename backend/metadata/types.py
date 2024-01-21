from typing import Optional

from pydantic import BaseModel
from strenum import StrEnum


class IsoLang(StrEnum):
    RU = "ru"
    EN = "en"
    HE = "he"  # hebrew


TextSourceKey = str


class TextSource(BaseModel):
    key: TextSourceKey  # key used hroughout the section
    mark: str  # short mark, conventionally in [brackets]
    description: str
    links: list[str]
    language: IsoLang


CommentSourceKey = str


class CommentSource(BaseModel):
    key: CommentSourceKey
    name: str
    links: list[str]
    language: IsoLang


class TanakhBookInfo(BaseModel):
    # for Torah: 1-based book number (1: Genesis, 2: Exodus, ...),
    # after that continues in ascending order (6: Joshua, 7: Judges, ...)
    id: int
    name: dict[TextSourceKey, str]


class ParshaInfo(BaseModel):
    id: int
    book_id: int
    chapter_verse_start: tuple[int, int]
    chapter_verse_end: tuple[int, int]
    name: dict[TextSourceKey, str]

    # only latin characters and dashes; used in urls like https://<base-url>/parsha/<url_name>
    url_name: str

    # "parsha" is constrained to a single book, but sometimes real weekly portion has several
    # of these "single-book parshas" (e.g. Seder Ha-Mishmarah puts Joel and Amos together in
    # a single "superparsha"). in this case parshas have this id set to the first of them (i.e. to Joel)
    parsha_group_leader_id: Optional[int] = None


class TanakhSectionMetadata(BaseModel):
    title: dict[TextSourceKey, str]
    subtitle: Optional[dict[TextSourceKey, str]]
    text_sources: list[TextSource]
    comment_sources: list[CommentSource]
    books: list[TanakhBookInfo]
    parshas: list[ParshaInfo]
