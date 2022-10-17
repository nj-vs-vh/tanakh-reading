"""Parser for https://lechaim.ru/torah/"""


import json
from pathlib import Path
from typing import cast
from bs4 import BeautifulSoup, Tag
import requests  # type: ignore
from merge import merge_and_save_parsha_data
from model import ChapterData, ParshaData, VerseData

from metadata import TextSource, get_book_by_parsha
from utils import inner_tag_text, tag_filter


HTML_DIR = Path("html/lechaim")
HTML_DIR.mkdir(exist_ok=True)


def get_per_day_htmls(parsha: int, parsha_url_path: str) -> list[BeautifulSoup]:
    parsha_htmls_dir = HTML_DIR / str(parsha)
    parsha_htmls_dir.mkdir(exist_ok=True)

    res: list[BeautifulSoup] = []
    for day in range(1, 8):
        html = parsha_htmls_dir / f"day{day}.html"
        if not html.exists():
            url = f"https://lechaim.ru/academy/{parsha_url_path}{day}/"
            print(f"Downloading parsha HTML for day {day} from {url}...")
            resp = requests.get(url)
            if resp.status_code != 200:
                raise ValueError(f"Non-200 status for {resp}")
            html.write_bytes(resp.content)
        res.append(BeautifulSoup(html.read_text(), features="html.parser"))
    return res


def parse(parsha: int, parsha_url_path: str):
    parsha_data = ParshaData(
        book=get_book_by_parsha(parsha),
        parsha=parsha,
        chapters=[]
    )

    chapter_data_by_chapter: dict[int, ChapterData] = dict()

    parsha_day_docs = get_per_day_htmls(parsha, parsha_url_path)
    for parsha_day_doc in parsha_day_docs:
        for chapter_container in parsha_day_doc.find_all(tag_filter("div", ["article-part_text"])):
            chapter_container = cast(Tag, chapter_container)
            chapter_header = chapter_container.find(tag_filter("h3", ["article-part_title"]))

            chapter = int(inner_tag_text(chapter_header).removeprefix("Глава").strip())
            if chapter in chapter_data_by_chapter:
                chapter_data = chapter_data_by_chapter[chapter]
                add_chapter_to_parsha = False
            else:
                chapter_data = ChapterData(
                    chapter=chapter,
                    verses=[],
                )
                chapter_data_by_chapter[chapter] = chapter_data
                add_chapter_to_parsha = True
            for verse_container in chapter_container.find_all(tag_filter("li", ["article-part_item"])):
                verse_container = cast(Tag, verse_container)
                verse_number_el = verse_container.find(tag_filter("input", []))
                verse_text_container = verse_container.find(tag_filter("div", ["article-part_translated"]))
                verse_data = VerseData(
                    verse=int(verse_number_el.attrs["value"]),
                    text={
                        TextSource.LECHAIM: inner_tag_text(verse_text_container),
                    },
                    comments={},
                )

                # comment parsing here
                chapter_data["verses"].append(verse_data)
            if add_chapter_to_parsha:
                parsha_data["chapters"].append(chapter_data)

    Path('ex.json').write_text(json.dumps(parsha_data, ensure_ascii=False, indent=2))

    merge_and_save_parsha_data(parsha, parsha_data)


if __name__ == "__main__":
    parse(2, "noach")
