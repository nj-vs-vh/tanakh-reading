# backwards compatibility
import itertools

from backend.metadata.neviim import NEVIIM_METADATA
from backend.metadata.torah import *  # noqa: F403, F401
from backend.metadata.torah import TORAH_METADATA
from backend.metadata.types import IsoLang

ALL_METADATA = [TORAH_METADATA, NEVIIM_METADATA]


def get_book_by_parsha(parsha: int) -> int:
    for parsha_info in itertools.chain.from_iterable(m.parshas for m in ALL_METADATA):
        if parsha_info.id == parsha:
            return parsha_info.book_id

    raise ValueError(f"No Tanakh book found for parsha {parsha}")


def get_text_source_language(text_source_key: str) -> IsoLang:
    for section in [TORAH_METADATA, NEVIIM_METADATA]:
        for ts in section.text_sources:
            if ts.key == text_source_key:
                return ts.language
    raise ValueError(f"Unknown text source key {text_source_key}!")


def get_comment_source_language(comment_source_key: str) -> IsoLang:
    for section in [TORAH_METADATA, NEVIIM_METADATA]:
        for cs in section.comment_sources:
            if cs.key == comment_source_key:
                return cs.language
    raise ValueError(f"Unknown text source key {comment_source_key}!")
