from itertools import chain

from aiohttp import web

from backend import metadata
from backend.database.interface import DatabaseInterface
from backend.model import CommentCoords, CommentData, ParshaData, VerseData


class ValidationError(web.HTTPBadRequest):
    def __init__(self, message: str) -> None:
        super().__init__(reason=message)


def validate_parsha(book: int, parsha: int):
    book_parsha_range = metadata.torah_book_parsha_ranges.get(book)
    if book_parsha_range is None:
        raise ValidationError(f"Book #{book} does not exist in the Torah")
    first_parsha, next_to_last_parsha = book_parsha_range
    if not (first_parsha <= parsha < next_to_last_parsha):
        raise ValidationError(f"Parsha #{parsha} is not in the book #{book}")


async def lookup_parsha_data(parsha: int, db: DatabaseInterface) -> ParshaData:
    parsha_data = await db.get_parsha_data(parsha)
    if parsha_data is None:
        raise ValidationError(f"Parsha {parsha} is not yet available")
    else:
        return parsha_data


async def lookup_verse_data(parsha_data: ParshaData, chapter: int, verse: int) -> VerseData:
    chapter_data_matches = [
        chapter_data for chapter_data in parsha_data["chapters"] if chapter_data["chapter"] == chapter
    ]
    if not chapter_data_matches:
        raise ValidationError(f"Chapter {chapter} is not in the parsha #{parsha_data['parsha']}")
    chapter_data = chapter_data_matches[0]
    verse_data_matches = [verse_data for verse_data in chapter_data["verses"] if verse_data["verse"] == verse]
    if not verse_data_matches:
        raise ValidationError(f"Verse {verse} is not in the chapter {chapter}")
    return verse_data_matches[0]


async def lookup_comment_data(verse_data: VerseData, comment_id: str) -> CommentData:
    comment_data_by_id = {cd["id"]: cd for cd in chain.from_iterable(verse_data["comments"].values())}
    comment_data = comment_data_by_id.get(comment_id)
    if comment_data is None:
        raise ValidationError(f"Comment with id {comment_id} does not exist")
    else:
        return comment_data


async def validate_comment_coords(comment_coords: CommentCoords, db: DatabaseInterface):
    parsha_data = await lookup_parsha_data(comment_coords.parsha, db)
    verse_data = await lookup_verse_data(parsha_data, comment_coords.chapter, comment_coords.verse)
    await lookup_comment_data(verse_data, comment_coords.comment_id)
