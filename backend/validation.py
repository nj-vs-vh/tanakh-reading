from itertools import chain

from aiohttp import web

from backend import metadata
from backend.model import CommentCoords, VerseData
from backend.static import get_parsha_data


class ValidationError(web.HTTPBadRequest):
    def __init__(self, message: str) -> None:
        super().__init__(reason=message)


def get_verse_data(book: int, parsha: int, chapter: int, verse: int) -> VerseData:
    book_parsha_range = metadata.torah_book_parsha_ranges.get(book)
    if book_parsha_range is None:
        raise ValidationError(f"Book #{book} does not exist in Torah")
    first_parsha, next_to_last_parsha = book_parsha_range
    if not (first_parsha <= parsha < next_to_last_parsha):
        raise ValidationError(f"Parsha #{parsha} is not in the book #{book}")
    parsha_data = get_parsha_data(parsha)
    if parsha_data is None:
        raise ValidationError(f"Parsha {parsha} is not yet available")
    chapter_data_matches = [
        chapter_data for chapter_data in parsha_data["chapters"] if chapter_data["chapter"] == chapter
    ]
    if not chapter_data_matches:
        raise ValidationError(f"Chapter {chapter} is not in the parsha #{parsha}")
    chapter_data = chapter_data_matches[0]
    verse_data_matches = [verse_data for verse_data in chapter_data["verses"] if verse_data["verse"] == verse]
    if not verse_data_matches:
        raise ValidationError(f"Verse {verse} is not in the chapter {chapter}")
    return verse_data_matches[0]


def validate_comment_coords(comment: CommentCoords):
    verse_data = get_verse_data(comment.book, comment.parsha, comment.chapter, comment.verse)
    verse_comment_ids = {comment_data["id"] for comment_data in chain.from_iterable(verse_data["comments"].values())}
    if comment.comment_id not in verse_comment_ids:
        raise ValidationError("Comment does not exist")
