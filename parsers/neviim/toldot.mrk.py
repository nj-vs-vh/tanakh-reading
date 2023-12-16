import argparse
import itertools
import os
import re
import traceback
from pathlib import Path

import bs4  # type: ignore
import requests  # type: ignore

from backend.database.mongo import texts_and_comments_to_parsha_data
from backend.metadata.neviim import MRK_SOURCE, NEVIIM_METADATA
from backend.metadata.types import IsoLang
from backend.model import ParshaData, StoredText, TextCoords
from parsers.merge import merge_parsha_data

SCRIPT_DIR = Path(__file__).parent
HTML_DIR = SCRIPT_DIR / "../../html/neviim/mrk"
HTML_DIR.mkdir(parents=True, exist_ok=True)


def parse_book(book_id: int, urlname: str):
    expected_book = next(b for b in NEVIIM_METADATA.books if b.id == book_id)
    print(f"Book info: {expected_book}")

    parsha_infos = [p for p in NEVIIM_METADATA.parshas if p.book_id == book_id]
    print("Parsha info: ")
    print(*parsha_infos, sep="\n")

    file = HTML_DIR / f"{book_id}.html"
    if not file.exists():
        resp = requests.get(f"https://toldot.com/limud/library/neviim/{urlname}/")
        print(resp)
        file.write_text(resp.text)

    soup = bs4.BeautifulSoup(markup=file.read_text(), features="html.parser")
    article_body = soup.find("span", attrs={"class": "articletext rt"})
    assert isinstance(article_body, bs4.Tag)
    chapter_headers: list[bs4.Tag] = list(article_body.find_all("h3"))
    chapter_boundaries = chapter_headers + [None]
    expected_chapter_num = 1
    texts: list[StoredText] = []
    for h1, h2 in itertools.pairwise(chapter_boundaries):
        try:
            chapter_num = int(h1.get_text(separator=" ", strip=True))
            assert (
                chapter_num == expected_chapter_num
            ), f"Unexpected chapter number {chapter_num} (expected {expected_chapter_num})"
            expected_chapter_num += 1
            chapter_paragraphs: list[bs4.Tag] = []
            for sibling in h1.next_siblings:
                if sibling == h2:
                    break
                else:
                    chapter_paragraphs.append(sibling)
            assert chapter_paragraphs
            chapter_text = " ".join(p.get_text(separator=" ", strip=True) for p in chapter_paragraphs)
            chapter_text = re.sub(r"\s+", " ", chapter_text, flags=re.MULTILINE)
            chapter_text = chapter_text.strip()
            verses: list[str] = []
            for verse_num_match, next_verse_start in itertools.pairwise(
                itertools.chain(
                    re.finditer(r"\(\s*(\d+)\s*\)", chapter_text),
                    [None],
                )
            ):
                assert verse_num_match is not None
                verse_num = int(verse_num_match.group(1))
                verse_start_pos = verse_num_match.end()
                verse_text = (
                    chapter_text[verse_start_pos : next_verse_start.start()]  # noqa: E203
                    if next_verse_start is not None
                    else chapter_text[verse_start_pos:]
                ).strip()
                expected_verse_num = len(verses) + 1
                assert (
                    verse_num == expected_verse_num
                ), f"Unexpected verse number {verse_num} ({expected_verse_num = }, {verse_text!r})"
                verses.append(verse_text)
                parsha_info = next(
                    (p for p in parsha_infos if p.chapter_verse_start[0] <= chapter_num <= p.chapter_verse_end[0]), None
                )
                assert parsha_info is not None, "Unexpected parsed text coords, no parsha info found"
                texts.append(
                    StoredText(
                        text_coords=TextCoords(parsha=parsha_info.id, chapter=chapter_num, verse=verse_num),
                        text_source=MRK_SOURCE,
                        text=verse_text,
                        language=IsoLang.RU,
                    )
                )
        except Exception:
            print(f"Error parsing chapter between {h1} and {h2}")
            traceback.print_exc()
            return

    texts.sort(key=lambda t: t.text_coords.parsha)
    parsha_data_list: list[ParshaData] = []
    for _, parsha_texts in itertools.groupby(texts, key=lambda t: t.text_coords.parsha):
        parsha_data_list.append(texts_and_comments_to_parsha_data(list(parsha_texts), []))

    if len(parsha_data_list) != len(parsha_infos):
        raise ValueError(f"Unexpected number of parshas parsed {len(parsha_data_list) = } {len(parsha_infos) = }")

    for parsha_data in parsha_data_list:
        print(f"Downloading existing data for {parsha_data['parsha']}...")
        response = requests.get(f"{os.environ['BASE_URL']}/parsha/{parsha_data['parsha']}")
        if response.status_code == 404:
            print("No such parsha, uploading for the first time, OK")
        elif response.status_code == 200:
            print("Parsha data exists, validating it")
            existing_parsha_data = response.json()
            merge_parsha_data(existing_parsha_data, parsha_data)
        print("Uploading parsha data...")
        response = requests.put(
            f"{os.environ['BASE_URL']}/parsha",
            json=parsha_data,
            headers={"X-Admin-Token": os.environ["ADMIN_TOKEN"]},
        )
        print(f"Response: {response}")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("book_idx", type=int)
    argparser.add_argument("book_url_name", type=str)
    args = argparser.parse_args()

    parse_book(args.book_idx, args.book_url_name)
