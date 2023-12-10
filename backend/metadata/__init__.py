# backwards compatibility
from backend.metadata.torah import *  # noqa: F403, F401
from backend.metadata.torah import TORAH_METADATA


def get_book_by_parsha(parsha: int) -> int:
    for parsha_info in TORAH_METADATA.parshas:
        if parsha_info.id == parsha:
            return parsha_info.book_id

    raise ValueError(f"No Torah book found for parsha {parsha}")
