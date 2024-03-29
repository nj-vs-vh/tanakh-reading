"""Parser for https://reformjudaism.org/learning/torah-study/english-translations-torah-portions """


import argparse
import re
from typing import Optional

import requests  # type: ignore
from bs4 import BeautifulSoup, Tag  # type: ignore

from backend import metadata
from backend.model import ChapterData, ParshaData, VerseData
from parsers.merge import merge_and_save_parsha_data
from parsers.utils import HTML_DIR as COMMON_HTML_DIR
from parsers.utils import collapse_whitespace, inner_tag_text

HTML_DIR = COMMON_HTML_DIR / "reformjudaism"
HTML_DIR.mkdir(exist_ok=True)
LISTING_HTML = HTML_DIR / "listing.html"

BASE_URL = "https://reformjudaism.org"


def get_listing_html() -> BeautifulSoup:
    if not LISTING_HTML.exists():
        print("Downloading listing")
        resp = requests.get(f"{BASE_URL}/learning/torah-study/english-translations-torah-portions")
        LISTING_HTML.write_bytes(resp.content)
    return BeautifulSoup(LISTING_HTML.read_text(), features="html.parser")


def get_url(parsha_no: int):
    parsha_name = metadata.parsha_names[parsha_no][metadata.TorahTextSource.PLAUT]
    print(f"Full parsha name: {parsha_name!r}")
    parsha_name = parsha_name.split("(")[0].strip()
    print(f"Parsha name on link: {parsha_name!r}")
    listing = get_listing_html()
    for el in listing.descendants:
        if inner_tag_text(el) == parsha_name and isinstance(el, Tag) and el.name == "a":
            parsha_href = el.attrs["href"]
            if parsha_href.startswith("http"):
                print(f"Found URL for parsha: {parsha_href!r}")
                return parsha_href
            else:
                print(f"Found path for parsha: {parsha_href!r}")
                return BASE_URL + parsha_href
    raise ValueError(f"Parsha not found by name: {parsha_name}")


def parse(parsha: int):
    html_file = HTML_DIR / f"{parsha}.html"
    if not html_file.exists():
        url = get_url(parsha)
        resp = requests.get(url)
        html_file.write_bytes(resp.content)
    main = BeautifulSoup(html_file.read_text(), features="html.parser")

    def looks_like_text_container(tag: Tag) -> bool:
        return isinstance(tag, Tag) and "text-formatted" in tag.attrs.get("class", [])

    text_container = main.find(looks_like_text_container)
    if text_container is None:
        raise ValueError("Can't find text container")

    parsha_data = ParshaData(
        book=metadata.get_book_by_parsha(parsha),
        parsha=parsha,
        chapters=[],
    )
    current_chapter_data: Optional[ChapterData] = None
    current_verse_data: Optional[VerseData] = None
    expected_next_verse = -1
    for child in text_container.descendants:
        text_part = inner_tag_text(child)
        if not text_part:
            continue
        if isinstance(child, Tag):
            continue

        chapter_start_match = re.match(r"(\d+):(\d+)\]", text_part)
        if chapter_start_match is not None:
            if current_chapter_data is not None:
                if current_verse_data is not None:
                    current_chapter_data["verses"].append(current_verse_data)
                parsha_data["chapters"].append(current_chapter_data)
            current_chapter_data = ChapterData(
                chapter=int(chapter_start_match.group(1)),
                verses=[],
            )
            current_verse = int(chapter_start_match.group(2))
            current_verse_data = VerseData(
                verse=current_verse,
                text={metadata.TorahTextSource.PLAUT: ""},
                comments={},
            )
            expected_next_verse = current_verse + 1
            continue

        verse_start_match = re.match(rf"({expected_next_verse})\]", text_part)
        if verse_start_match is not None:
            if current_chapter_data is not None and current_verse_data is not None:
                current_chapter_data["verses"].append(current_verse_data)
            current_verse_data = VerseData(
                verse=int(verse_start_match.group(1)),
                text={metadata.TorahTextSource.PLAUT: ""},
                comments={},
            )
            expected_next_verse += 1
            continue

        if current_verse_data is not None:
            current_verse_data["text"][metadata.TorahTextSource.PLAUT] += collapse_whitespace(text_part)

    if current_chapter_data is not None:
        if current_verse_data is not None:
            current_chapter_data["verses"].append(current_verse_data)
        parsha_data["chapters"].append(current_chapter_data)

    merge_and_save_parsha_data(parsha, parsha_data)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("parsha_index", type=int)
    args = argparser.parse_args()
    parse(args.parsha_index)
