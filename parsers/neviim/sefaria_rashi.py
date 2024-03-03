import argparse
import itertools
import json
import os
import re
from pathlib import Path

import bs4  # type: ignore
import requests  # type: ignore

from backend.database.mongo import texts_and_comments_to_parsha_data
from backend.metadata.neviim import JPS_GSE_SOURCE, NEVIIM_METADATA
from backend.metadata.types import IsoLang
from backend.model import ParshaData, StoredText, TextCoords
from parsers.merge import merge_parsha_data
from parsers.utils import collapse_whitespace, dump_parsha

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR / "../.."
SOURCE_JSON_DIR = PROJECT_ROOT / "json/neviim/rashi-on-neviim"
SOURCE_JSON_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR = PROJECT_ROOT / "json/neviim/jps"
JSON_DIR.mkdir(parents=True, exist_ok=True)

JSON_PATHS = {
    6: SOURCE_JSON_DIR / "Rashi on Joshua - en - The Book of Joshua, Metsudah Publications, 1997.json",
}


# TODO!!!


def parse_comments(book_id: int, upload: bool):
    json_path = JSON_PATHS[book_id]
    assert json_path.exists(), json_path
    expected_book = next(b for b in NEVIIM_METADATA.books if b.id == book_id)
    print(f"Book info: {expected_book}")
    print()

    parsha_infos = [p for p in NEVIIM_METADATA.parshas if p.book_id == book_id]
    print("Parsha info: ")
    print(*parsha_infos, sep="\n")
    print()

    print("Reading data from JSON...")
    data = json.loads(json_path.read_text())
    texts_raw: list[list[str]] = data["text"]
    texts: list[StoredText] = []
    for chapter_idx, verses in enumerate(texts_raw):
        chapter_num = chapter_idx + 1
        for verse_idx, verse_text_raw in enumerate(verses):
            verse_text_soup = bs4.BeautifulSoup(verse_text_raw, features="html.parser")
            redundant_elements: list[bs4.Tag] = []
            for element in verse_text_soup.descendants:
                if isinstance(element, bs4.Tag) and (
                    # removing footnotes-related stuff because there's no way to render them right now
                    element.name == "sup"
                    or any("footnote" in css_class for css_class in element.attrs.get("class", []))
                ):
                    redundant_elements.append(element)
            for e in redundant_elements:
                e.decompose()
            verse_text = str(verse_text_soup)
            verse_text = re.sub(r"\s*\—\s*", " — ", verse_text)
            verse_text = verse_text.strip()
            verse_text = collapse_whitespace(verse_text)
            # print("\n", verse_text_raw, "\n", verse_text, "\n", sep="")

            verse_num = verse_idx + 1
            parsha_info = next(
                (p for p in parsha_infos if p.chapter_verse_start[0] <= chapter_num <= p.chapter_verse_end[0]), None
            )
            assert parsha_info is not None, "Unexpected parsed text coords, no parsha info found"
            texts.append(
                StoredText(
                    text_coords=TextCoords(parsha=parsha_info.id, chapter=chapter_num, verse=verse_num),
                    text_source=JPS_GSE_SOURCE,
                    text=verse_text,
                    language=IsoLang.RU,
                    format="html",
                )
            )

    texts.sort(key=lambda t: t.text_coords.parsha)
    parsha_data_list: list[ParshaData] = []
    for _, parsha_texts in itertools.groupby(texts, key=lambda t: t.text_coords.parsha):
        parsha_data_list.append(texts_and_comments_to_parsha_data(list(parsha_texts), []))

    if len(parsha_data_list) != len(parsha_infos):
        raise ValueError(f"Unexpected number of parshas parsed {len(parsha_data_list) = } {len(parsha_infos) = }")

    for parsha_data in parsha_data_list:
        print("Saving JSON")
        (JSON_DIR / f"parsha-{parsha_data['parsha']}.json").write_text(dump_parsha(parsha_data))

        print(f"Downloading existing data for {parsha_data['parsha']} to validate...")
        response = requests.get(f"{os.environ['BASE_URL']}/parsha/{parsha_data['parsha']}")
        if response.status_code == 404:
            print("No such parsha, skipping validation")
        elif response.status_code == 200:
            print("Parsha data exists, validating it")
            existing_parsha_data = response.json()
            try:
                merge_parsha_data(existing_parsha_data, parsha_data)
            except Exception as e:
                print(f"Validation failed: {e!r}, skipping the parsha")
                continue

        if upload:
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
    argparser.add_argument("--upload", action="store_true", default=False)
    args = argparser.parse_args()

    parse_comments(args.book_idx, args.upload)
