from aiohttp import web

from backend import metadata


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
