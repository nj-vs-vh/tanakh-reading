from typing import Literal, Optional, TypedDict


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
