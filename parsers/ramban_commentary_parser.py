""" Parser for JSON dumps downloaded from https://www.sefaria.org/

Download per-book-json from https://www.sefaria.org/texts/Tanakh/Rishonim%20on%20Tanakh/Ramban/Torah
"""

import argparse
import json

from bs4 import BeautifulSoup  # type: ignore

from backend import metadata
from backend.model import CommentData, ParshaData
from parsers.local_storage import JSON_DIR, parsha_path
from parsers.utils import dump_parsha, has_class

JSON_DUMPS_PER_BOOK = {
    1: JSON_DIR
    / "Ramban on Genesis - en - Commentary on the Torah by Ramban (Nachmanides). Translated and annotated by Charles B. Chavel. New York, Shilo Pub. House, 1971-1976.json",  # noqa: E501
    2: JSON_DIR
    / "Ramban on Exodus - en - Commentary on the Torah by Ramban (Nachmanides). Translated and annotated by Charles B. Chavel. New York, Shilo Pub. House, 1971-1976.json",  # noqa: E501
    3: JSON_DIR
    / "Ramban on Leviticus - en - Commentary on the Torah by Ramban (Nachmanides). Translated and annotated by Charles B. Chavel. New York, Shilo Pub. House, 1971-1976.json",  # noqa: E501
    4: JSON_DIR
    / "Ramban on Numbers - en - Commentary on the Torah by Ramban (Nachmanides). Translated and annotated by Charles B. Chavel. New York, Shilo Pub. House, 1971-1976.json",  # noqa: E501
    5: JSON_DIR
    / "Ramban on Deuteronomy - en - Commentary on the Torah by Ramban (Nachmanides). Translated and annotated by Charles B. Chavel. New York, Shilo Pub. House, 1971-1976.json",  # noqa: E501
}


def parse_ramban_commentaries(parsha_index: int):
    book = metadata.get_book_by_parsha(parsha_index)
    try:
        ramban_commentary_raw = json.loads(JSON_DUMPS_PER_BOOK[book].read_text())
    except Exception as e:
        raise RuntimeError(f"Eror reading Ramban Commentary: {e!r}")
    try:
        parsha_data: ParshaData = json.loads(parsha_path(parsha_index).read_text())
    except Exception as e:
        raise RuntimeError(f"Eror reading parsha data: {e!r}")

    # making temp copy to trace changes
    # shutil.copy(
    #     parsha_path(parsha_index),
    #     parsha_path(parsha_index).with_suffix(".json.temp"),
    # )

    ramban_commentary: list[list[list[str]]] = ramban_commentary_raw["text"][""]
    print(f"Ramban commentary chapters: {len(ramban_commentary)}")
    for chapter_data in parsha_data["chapters"]:
        if chapter_data["chapter"] <= len(ramban_commentary):
            ramban_chapter = ramban_commentary[chapter_data["chapter"] - 1]  # 1-based -> 0-based
        else:
            print(
                f"Chapter #{chapter_data['chapter']} is out of bounds "
                + f"for available Ramban commentary ({len(ramban_commentary)})"
            )
            continue
        for verse_data in chapter_data["verses"]:
            if verse_data["verse"] <= len(ramban_chapter):
                ramban_verse = ramban_chapter[verse_data["verse"] - 1]  # 1-based -> 0-based
            else:
                print(
                    f"Verse #{verse_data['verse']} is out of bounds "
                    + f"for available Ramban commentary ({len(ramban_chapter)}) "
                    + f"in chapter {chapter_data['chapter']}, assuming no commentaries for the verse"
                )
                ramban_verse = []
            ramban_comments: list[CommentData] = []
            for ramban_comment_raw in ramban_verse:
                # comments have the following structure:
                # > IN THE BEGINNING G-D CREATED. Rashi wrote: “This verse calls aloud for elucidation ...
                # all-caps part is anchor phrase, the rest is the comment body
                for word in ramban_comment_raw.split():
                    if word.upper() != word:
                        break
                print(f"Split word (first non-caps): {word}")
                anchor_phrase = ramban_comment_raw.split(word)[0]
                comment_body_raw = ramban_comment_raw.removeprefix(anchor_phrase).strip()
                anchor_phrase = anchor_phrase.strip()
                print(f"Anchor phrase: {anchor_phrase!r}")
                print(f"Comment: {comment_body_raw[:40]}...")

                ramban_comment_bs = BeautifulSoup(comment_body_raw, features="html.parser")
                comment_body = ""
                for tag in ramban_comment_bs.children:
                    if has_class(tag, "footnote-marker"):
                        pass
                    elif has_class(tag, "footnote"):
                        comment_body += " (" + str(tag) + ") "
                    else:
                        comment_body += str(tag)
                ramban_comments.append(
                    CommentData(
                        anchor_phrase=anchor_phrase,
                        comment=comment_body,
                        format="html",
                    )
                )

            if ramban_comments:
                verse_data["comments"][metadata.CommentSource.RAMBAN] = ramban_comments

    parsha_path(parsha_index).write_text(dump_parsha(parsha_data))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("parsha_index", type=int)
    args = argparser.parse_args()
    parse_ramban_commentaries(args.parsha_index)
