""" Parser for JSON dumps downloaded from https://www.sefaria.org/

Download per-book-json from https://www.sefaria.org/texts/Tanakh/Acharonim%20on%20Tanakh/Or%20HaChaim/Torah
"""

import argparse
import json
from re import L

import bs4  # type: ignore

from backend import metadata
from backend.model import CommentData, ParshaData
from parsers.identification import ensure_comment_ids
from parsers.local_storage import JSON_DIR, parsha_path
from parsers.utils import dump_parsha, has_class

JSON_DUMPS_PER_BOOK = {
    1: JSON_DIR / "Or HaChaim on Genesis - en - Or Hachayim, trans. Eliyahu Munk.json",
    2: JSON_DIR / "Or HaChaim on Exodus - en - Or Hachayim, trans. Eliyahu Munk.json",
    3: JSON_DIR / "Or HaChaim on Leviticus - en - Or Hachayim, trans. Eliyahu Munk.json",
    4: JSON_DIR / "Or HaChaim on Numbers - en - Or Hachayim, trans. Eliyahu Munk.json",
    5: JSON_DIR / "Or HaChaim on Deuteronomy - en - Or Hachayim, trans. Eliyahu Munk.json",
}


def parse_or_hachaim_commentaries(parsha_index: int):
    book = metadata.get_book_by_parsha(parsha_index)
    try:
        commentary_raw = json.loads(JSON_DUMPS_PER_BOOK[book].read_text())
    except Exception as e:
        raise RuntimeError(f"Eror reading file: {e!r}")
    try:
        parsha_data: ParshaData = json.loads(parsha_path(parsha_index).read_text())
    except Exception as e:
        raise RuntimeError(f"Eror reading parsha data: {e!r}")

    commentary: list[list[list[str]]] = commentary_raw["text"][""] if book == 1 else commentary_raw["text"]
    print(f"Commentary chapters: {len(commentary)}")
    for chapter_data in parsha_data["chapters"]:
        if chapter_data["chapter"] <= len(commentary):
            chapter = commentary[chapter_data["chapter"] - 1]  # 1-based -> 0-based
        else:
            print(
                f"Chapter #{chapter_data['chapter']} is out of bounds "
                + f"for available commentary ({len(commentary)})"
            )
            continue
        for verse_data in chapter_data["verses"]:
            if verse_data["verse"] <= len(chapter):
                verse = chapter[verse_data["verse"] - 1]  # 1-based -> 0-based
            else:
                print(
                    f"Verse #{verse_data['verse']} is out of bounds "
                    + f"for available commentary ({len(chapter)}) "
                    + f"in chapter {chapter_data['chapter']}, assuming no commentaries for the verse"
                )
                verse = []
            parsed_comments: list[CommentData] = []
            for parsed_comment_raw in verse:
                if not parsed_comment_raw:
                    continue
                parsed_comment_bs = bs4.BeautifulSoup(parsed_comment_raw, features="html.parser")
                parsed_comment_children_iter = iter(parsed_comment_bs.children)
                first_child = next(parsed_comment_children_iter)
                if isinstance(first_child, bs4.Tag) and first_child.name == "b":
                    comment_body = ""
                    for child in parsed_comment_children_iter:
                        comment_body += str(child)
                    comment_body = comment_body.strip()
                    print(f"Comment with anchor: {first_child!r};\n\tbody: {comment_body[:60] + '...'!r}")
                    parsed_comments.append(
                        CommentData(
                            anchor_phrase=str(first_child.get_text(separator=" ", strip=True)),
                            comment=comment_body,
                            format="html",
                        )
                    )
                else:
                    print(f"Anchorless comment: {parsed_comment_raw[:60] + '...'!r}")
                    parsed_comments.append(
                        CommentData(
                            anchor_phrase=None,
                            comment=parsed_comment_raw,
                            format="html",
                        )
                    )

            if parsed_comments:
                verse_data["comments"][metadata.Commenter.OR_HACHAIM] = parsed_comments

    ensure_comment_ids(parsha_data)
    parsha_path(parsha_index).write_text(dump_parsha(parsha_data))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("parsha_index", type=int)
    args = argparser.parse_args()
    parse_or_hachaim_commentaries(args.parsha_index)
