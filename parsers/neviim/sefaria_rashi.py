"""
This script
(1) parses Rashi comments to Neviim from Sefaria Json dumps
(2) downloads the relevant parsha data from remote server
(3) inserts comments into it (accroding to a particular strategy)
(4) optionally, uploads, the updated parsha data back to the remote server
"""

import argparse
import copy
import enum
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
    12: SOURCE_JSON_DIR
    / "Rashi on Jeremiah - en - The Judaica Press complete Tanach with Rashi, translated by A. J. Rosenberg.json",
    13: SOURCE_JSON_DIR
    / "Rashi on Ezekiel - en - The Judaica Press complete Tanach with Rashi, translated by A. J. Rosenberg.json",
    14: SOURCE_JSON_DIR
    / "Rashi on Isaiah - en - The Judaica Press complete Tanach with Rashi, translated by A. J. Rosenberg.json",
}


class CommentInsertionMode(enum.Enum):
    append = "append"
    append_validate_empty = "append_validate_empty"
    replace_texts = "replace_texts"


def parse_comments(book_id: int, comment_insertion_mode: CommentInsertionMode, upload: bool):
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
    parsed_comments: list[StoredComment] = []
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
                            print(f"Discarding superscripted element: {element}")
                            continue
                        elif element.name == "i":
                            if "footnote" in element.attrs.get("class", ""):
                                comment_text_parts.append("(" + str(element).strip() + ")")
                            else:
                                comment_text_parts.append(str(element))
                        elif element.name in {"b", "span"}:
                            comment_text_parts.append(str(element))
                        else:
                            raise RuntimeError(f"Unexpected element: {element} ({comment_text_parts = })")
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
                parsed_comments.append(
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

    parsed_comments.sort(key=lambda c: c.text_coords.parsha)
    for parsha, parsed_parsha_comments_iter in itertools.groupby(parsed_comments, key=lambda c: c.text_coords.parsha):
        parsha = int(parsha)
        parsed_parsha_comments: list[StoredComment] = list(parsed_parsha_comments_iter)
        print(f"Parsha {parsha} has {len(parsed_parsha_comments)} comments")
        if not parsed_parsha_comments:
            continue

        parsed_parsha_comments.sort(key=lambda c: (c.text_coords.chapter, c.text_coords.verse))
        grouped_parsha_comments = itertools.groupby(
            parsed_parsha_comments, key=lambda c: (c.text_coords.chapter, c.text_coords.verse)
        )

        print("Downloading existing data for parsha")
        response = requests.get(f"{os.environ['BASE_URL']}/parsha/{parsha}")
        try:
            if response.status_code == 404:
                raise RuntimeError(
                    "No saved parsha, can't add parsed comments, please parse at least one text source first! "
                    + f"{response = }"
                )
            elif response.status_code != 200:
                raise RuntimeError(f"Unexpected status code: {response.status_code} " + f"{response = }")
            parsha_data: ParshaData = response.json()
            for (chapter_num, verse_num), comments_iter in grouped_parsha_comments:
                comments = list(comments_iter)
                matching_chapters = [c for c in parsha_data["chapters"] if c["chapter"] == chapter_num]
                if not matching_chapters:
                    raise RuntimeError(
                        f"Comments {comments} are attributed to chapter {chapter_num} "
                        + "but there is no such chapter in the existing parsha data"
                    )
                chapter = matching_chapters[0]
                matching_verses = [v for v in chapter["verses"] if v["verse"] == verse_num]
                if not matching_verses:
                    raise RuntimeError(
                        f"Comments {comments} are attributed to verse "
                        + f"{chapter_num}:{verse_num} "
                        + "but there is no such verse in the existing parsha data"
                    )
                verse = matching_verses[0]
                if comment_insertion_mode in {CommentInsertionMode.append, CommentInsertionMode.append_validate_empty}:
                    if comment_insertion_mode is CommentInsertionMode.append_validate_empty and verse["comments"].get(
                        RASHI_METSUDAH
                    ):
                        raise RuntimeError(
                            "comment insertion mode is append+validate empty, "
                            + f"but verse comments are not empty: {verse}"
                        )
                    verse["comments"].setdefault(RASHI_METSUDAH, []).extend(
                        [
                            {
                                "anchor_phrase": comment.anchor_phrase,
                                "comment": comment.comment,
                                "format": comment.format,
                            }
                            for comment in comments
                        ]
                    )

                elif comment_insertion_mode is CommentInsertionMode.replace_texts:
                    verse_comments = verse["comments"].get(RASHI_METSUDAH, [])
                    if len(verse_comments) != len(comments):
                        raise RuntimeError(
                            "comment insertion mode is replace texts, but verse comments and parsed comments "
                            + f"differ in length:\nexisting {len(verse_comments)}: {verse_comments}\n"
                            + f"parsed {len(comments)}: {comments}"
                        )
                    for vc, c in zip(verse_comments, comments):
                        vc["comment"] = c.comment
                        vc["anchor_phrase"] = c.anchor_phrase
                else:
                    raise RuntimeError(f"Unexpected comment insertion mode: {comment_insertion_mode}")
        except Exception:
            print("Unexpected error adding comments to parsha, ignoring it")
            traceback.print_exc()
            continue

        print("Saving parsha data with inserted comments")
        (JSON_DIR / f"parsha-{parsha}.json").write_text(dump_parsha(parsha_data))

        if upload:
            url = f"{os.environ['BASE_URL']}/parsha"
            headers = {"X-Admin-Token": os.environ["ADMIN_TOKEN"]}
            if comment_insertion_mode is CommentInsertionMode.replace_texts:
                print("Uploading parsha data with POST request...")
                response = requests.post(url=url, json=parsha_data, headers=headers)
            else:
                parsha_data_update = copy.deepcopy(parsha_data)
                for chapter in parsha_data_update["chapters"]:
                    for verse in chapter["verses"]:
                        verse.get("text_formats", {}).clear()
                        verse.get("text", {}).clear()
                        verse.get("text_ids", {}).clear()
                        verse["comments"] = {k: v for k, v in verse["comments"].items() if k == RASHI_METSUDAH}
                print("Uploading parsha data with PUT request...")
                response = requests.put(url=url, json=parsha_data_update, headers=headers)
            print(f"Response: {response}")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("book_idx", type=int)
    argparser.add_argument(
        "--comment-insertion-mode",
        default=CommentInsertionMode.append_validate_empty,
        type=CommentInsertionMode,
    )
    argparser.add_argument("--upload", action="store_true", default=False)
    args = argparser.parse_args()

    parse_comments(args.book_idx, args.comment_insertion_mode, args.upload)
