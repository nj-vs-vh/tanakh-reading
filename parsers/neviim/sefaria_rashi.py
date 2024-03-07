import argparse
import copy
import itertools
import json
import os
import traceback
from pathlib import Path
from typing import Optional

import bs4  # type: ignore
import requests  # type: ignore

from backend.metadata.neviim import NEVIIM_METADATA, RASHI_METSUDAH
from backend.metadata.types import IsoLang
from backend.model import ParshaData, StoredComment, TextCoords
from parsers.utils import dump_parsha

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR / "../.."
SOURCE_JSON_DIR = PROJECT_ROOT / "json/neviim/rashi-on-neviim"
SOURCE_JSON_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR = PROJECT_ROOT / "json/neviim/rashi-on-neviim-parsha-data"
JSON_DIR.mkdir(parents=True, exist_ok=True)

JSON_PATHS = {
    6: SOURCE_JSON_DIR / "Rashi on Joshua - en - The Book of Joshua, Metsudah Publications, 1997.json",
    7: SOURCE_JSON_DIR / "Rashi on Judges - en - The Metsudah Tanach series, Lakewood, N.J.json",
    8: SOURCE_JSON_DIR / "Rashi on I Samuel - en - The Metsudah Tanach series, Lakewood, N.J.json",
    9: SOURCE_JSON_DIR / "Rashi on II Samuel - en - The Metsudah Tanach series, Lakewood, N.J.json",
    10: SOURCE_JSON_DIR / "Rashi on I Kings - en - The Metsudah Tanach series, Lakewood, N.J.json",
    11: SOURCE_JSON_DIR / "Rashi on II Kings - en - The Metsudah Tanach series, Lakewood, N.J.json",
}


def parse_comments(book_id: int, upload: bool):
    json_path = JSON_PATHS[book_id]
    assert json_path.exists(), json_path
    book_info = next(b for b in NEVIIM_METADATA.books if b.id == book_id)
    print(f"Book info: {book_info}")
    print()

    parsha_infos = [p for p in NEVIIM_METADATA.parshas if p.book_id == book_id]
    print("Parsha info: ")
    print(*parsha_infos, sep="\n")
    print()

    print("Reading data from JSON...")
    data = json.loads(json_path.read_text())
    texts_raw: list[list[list[str]]] = data["text"]
    comments: list[StoredComment] = []
    for chapter_idx, verses in enumerate(texts_raw):
        chapter_num = chapter_idx + 1
        for verse_idx, comments_raw in enumerate(verses):
            for comment_idx, comment_text_raw in enumerate(comments_raw):
                comment_text_soup = bs4.BeautifulSoup(comment_text_raw, features="html.parser")
                anchor_phrase: Optional[str] = None
                comment_text_parts: list[str] = []
                for idx, element in enumerate(comment_text_soup.children):
                    if isinstance(element, bs4.Tag):
                        if idx == 0 and element.name == "b":
                            anchor_phrase = element.text
                        elif element.name == "sup":
                            continue
                        elif element.name == "i" and "footnote" in element.attrs.get("class", ""):
                            comment_text_parts.append("(" + str(element).strip() + ")")
                    else:
                        comment_text_parts.append(str(element).strip())
                comment_text = " ".join(comment_text_parts)

                # print(comment_text_raw)
                # print(f"{anchor_phrase = }")
                # print(f"{comment_text = }")
                # print("\n\n")

                verse_num = verse_idx + 1
                parsha_info = next(
                    (p for p in parsha_infos if p.chapter_verse_start[0] <= chapter_num <= p.chapter_verse_end[0]), None
                )
                assert parsha_info is not None, "Unexpected parsed text coords, no parsha info found"
                comments.append(
                    StoredComment(
                        text_coords=TextCoords(parsha=parsha_info.id, chapter=chapter_num, verse=verse_num),
                        comment_source=RASHI_METSUDAH,
                        comment=comment_text,
                        anchor_phrase=anchor_phrase,
                        index=comment_idx,
                        language=IsoLang.RU,
                        format="html",
                    )
                )

    for parsha, parsha_comments in itertools.groupby(comments, key=lambda c: c.text_coords.parsha):
        parsha = int(parsha)
        parsha_comments: list[StoredComment] = list(parsha_comments)
        print(f"Parsha {parsha} has {len(parsha_comments)} comments")
        if not parsha_comments:
            continue

        print("Downloading existing data for parsha")
        response = requests.get(f"{os.environ['BASE_URL']}/parsha/{parsha}")
        try:
            if response.status_code == 404:
                raise RuntimeError(
                    "No saved parsha, can't add parsed comments, please parse at least one text source first!"
                )
            elif response.status_code != 200:
                raise RuntimeError(f"Unexpected status code: {response.status_code}")
            parsha_data: ParshaData = response.json()
            for comment in parsha_comments:
                matching_chapters = [c for c in parsha_data["chapters"] if c["chapter"] == comment.text_coords.chapter]
                if not matching_chapters:
                    raise RuntimeError(
                        f"Comment {comment} is attributed to chapter {comment.text_coords.chapter} "
                        + "but there is no such chapter in the existing parsha data"
                    )
                chapter = matching_chapters[0]
                matching_verses = [v for v in chapter["verses"] if v["verse"] == comment.text_coords.verse]
                if not matching_verses:
                    raise RuntimeError(
                        f"Comment {comment} is attributed to verse "
                        + f"{comment.text_coords.chapter}:{comment.text_coords.verse} "
                        + "but there is no such verse in the existing parsha data"
                    )
                verse = matching_verses[0]
                verse["comments"].setdefault(RASHI_METSUDAH, []).append(
                    {
                        "anchor_phrase": comment.anchor_phrase,
                        "comment": comment.comment,
                        "format": comment.format,
                    }
                )
        except Exception:
            print("Unexpected error adding comments to parsha, ignoring it")
            traceback.print_exc()
            continue

        print("Saving parsha data with inserted comments")
        (JSON_DIR / f"parsha-{parsha}.json").write_text(dump_parsha(parsha_data))

        if upload:
            parsha_data_update = copy.deepcopy(parsha_data)
            for chapter in parsha_data_update["chapters"]:
                for verse in chapter["verses"]:
                    verse.get("text_formats", {}).clear()
                    verse.get("text", {}).clear()
                    verse.get("text_ids", {}).clear()
                    verse["comments"] = {k: v for k, v in verse["comments"].items() if k == RASHI_METSUDAH}
            print("Uploading parsha data...")
            response = requests.put(
                f"{os.environ['BASE_URL']}/parsha",
                json=parsha_data_update,
                headers={"X-Admin-Token": os.environ["ADMIN_TOKEN"]},
            )
            print(f"Response: {response}")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("book_idx", type=int)
    argparser.add_argument("--upload", action="store_true", default=False)
    args = argparser.parse_args()

    parse_comments(args.book_idx, args.upload)
