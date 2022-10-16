"""Parser for https://reformjudaism.org/learning/torah-study/english-translations-torah-portions"""


import argparse
import json
import re
from pathlib import Path
from typing import Optional

import requests  # type: ignore
from bs4 import BeautifulSoup, Tag

import metadata
from config import parsha_json
from merge import merge_parsha_data
from model import ChapterData, ParshaData, VerseData
from utils import collapse_whitespace, inner_tag_text

HTML_DIR = Path("html/reformjudaism")
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
    parsha_name = metadata.parsha_names[parsha_no][metadata.Translation.PLAUT]
    print(f"Parsha name: {parsha_name!r}")
    listing = get_listing_html()
    for el in listing.descendants:
        if inner_tag_text(el) == parsha_name and isinstance(el, Tag) and el.name == "a":
            parsha_path = el.attrs["href"]
            print(f"Found path for parsha: {parsha_path}")
            return BASE_URL + parsha_path


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
                text={metadata.Translation.PLAUT: ""},
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
                text={metadata.Translation.PLAUT: ""},
                comments={},
            )
            expected_next_verse += 1
            continue

        if current_verse_data is not None:
            current_verse_data["text"][metadata.Translation.PLAUT] += collapse_whitespace(text_part)

    if current_chapter_data is not None:
        if current_verse_data is not None:
            current_chapter_data["verses"].append(current_verse_data)
        parsha_data["chapters"].append(current_chapter_data)

    existing_parsha_data = json.loads(parsha_json(parsha).read_text())
    resulting_parsha_data = merge_parsha_data(existing_parsha_data, parsha_data)
    parsha_json(parsha).write_text(json.dumps(resulting_parsha_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("parsha_index", type=int)
    args = argparser.parse_args()
    parse(args.parsha_index)
