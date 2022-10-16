import re

import bs4


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
    if not isinstance(tag, bs4.Tag):
        return False
    return class_name in tag.attrs.get("class", [])


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
