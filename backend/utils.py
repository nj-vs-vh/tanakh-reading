import logging
import string
import unicodedata
from typing import Any, Hashable, Iterable, TypeVar

from aiohttp import web

logger = logging.getLogger(__name__)


async def safe_request_json(request: web.Request) -> dict[str, Any]:
    try:
        return await request.json()
    except Exception:
        logger.exception("Error parsing request JSON")
        raise web.HTTPBadRequest(reason="Request body must be a valid JSON within certain limits")


ItemT = TypeVar("ItemT", bound=Hashable)


def deduplicate_keeping_order(iterable: Iterable[ItemT]) -> list[ItemT]:
    seen = set[ItemT]()
    result = list[ItemT]()
    for item in iterable:
        if item in seen:
            continue
        result.append(item)
        seen.add(item)
    return result


ALPHABETS = {
    "en": set(string.ascii_lowercase),
    "ru": set("абвгдеёжзийклмнопрстуфхцчшщъыьэюя"),
}


def worst_language_detection_ever(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    scores = [(lang, len([ch for ch in s if ch in alphabet])) for lang, alphabet in ALPHABETS.items()]
    scores.sort(key=lambda l_s: l_s[1], reverse=True)
    top_lang, top_lang_score = next(iter(scores))
    if top_lang_score > 3:
        return top_lang
    else:
        return "none"
