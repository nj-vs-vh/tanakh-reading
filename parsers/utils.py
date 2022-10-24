import json
import re
from pathlib import Path
from typing import Callable

import bs4  # type: ignore

from backend.model import ParshaData

HTML_DIR = Path(__file__).parent / "../html"


def collapse_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def postprocess_patched_text(s: str) -> str:
    s = collapse_whitespace(s)
    s = re.sub(r"\s+([,.:;!?)])", r"\1", s)  # removing whitespace before punctuation
    s = re.sub(r"([('\"])\s+", r"\1", s)  # removing whitespace after punctuation
    s = s.strip()
    return s


def inner_tag_text(tag: bs4.Tag) -> str:
    if isinstance(tag, str):
        return collapse_whitespace(tag)
    elif isinstance(tag, bs4.Tag):
        return postprocess_patched_text(tag.get_text(separator=" ", strip=True))
    else:
        return str(tag).strip()


def strip_html_breaks(html_text: str) -> str:
    html_text = re.sub(r"^\s*(\s*<br\s*/>\s*)*\s*", "", html_text)
    html_text = re.sub(r"\s*(\s*<br\s*/>)*\s*$", "", html_text)
    return html_text


def has_class(tag: bs4.Tag, class_name: str) -> bool:
    return has_class_that(tag, lambda c: c == class_name)


def has_class_that(tag: bs4.Tag, predicate: Callable[[str], bool]) -> bool:
    if not isinstance(tag, bs4.Tag):
        return False
    return any(predicate(c) for c in tag.attrs.get("class", []))


def tag_filter(tag_name: str, required_classes: list[str]) -> Callable[[bs4.Tag], bool]:
    def predicate(tag: bs4.Tag) -> bool:
        if not isinstance(tag, bs4.Tag):
            return False
        else:
            return tag.name == tag_name and all(has_class(tag, c) for c in required_classes)

    return predicate


def are_strings_close(s1: str, s2: str) -> bool:
    s1 = collapse_whitespace(s1).lower()
    s2 = collapse_whitespace(s2).lower()
    if s1 == s2:
        return True
    if s1 in s2 or s2 in s1 and abs(len(s1) - len(s2)) < 3:
        True
    return False


def strip_leading_dot(s: str) -> str:
    return collapse_whitespace(s.removeprefix("."))


def dump_parsha(parsha_data: ParshaData) -> str:
    return json.dumps(parsha_data, ensure_ascii=False, indent=2)
