from typing import List, Literal, TypedDict, Union
import json
import argparse

from backend.model import ParshaData
from backend import metadata
from parsers.local_storage import JSON_DIR, parsha_path
from parsers.utils import dump_parsha


class TanakhWithNikkudDoc(TypedDict):
    status: Literal["locked"]
    versionTitle: Literal["Tanach with Nikkud"]
    license: Literal["Public Domain"]
    language: Literal["he"]
    title: str
    versionSource: str
    versionTitleInHebrew: Literal["תנ״ך עם ניקוד"]
    actualLanguage: Literal["he"]
    heTitle: str
    categories: List[Union[Literal["Tanakh"], Literal["Torah"]]]
    text: List[List[str]]
    sectionNames: List[Union[Literal["Chapter"], Literal["Verse"]]]


JSON_DUMPS_PER_BOOK = {
    1: JSON_DIR / "Genesis - he - Tanach with Nikkud.json",
    2: JSON_DIR / "Exodus - he - Tanach with Nikkud.json",
    3: JSON_DIR / "Leviticus - he - Tanach with Nikkud.json",
    4: JSON_DIR / "Numbers - he - Tanach with Nikkud.json",
    5: JSON_DIR / "Deuteronomy - he - Tanach with Nikkud.json",
}


def parse_hebrew_text(parsha_index: int):
    book = metadata.get_book_by_parsha(parsha_index)
    try:
        hebrew_text_doc: TanakhWithNikkudDoc = json.loads(JSON_DUMPS_PER_BOOK[book].read_text())
    except Exception as e:
        raise RuntimeError(f"Eror reading Ramban Commentary: {e!r}")
    try:
        parsha_data: ParshaData = json.loads(parsha_path(parsha_index).read_text())
    except Exception as e:
        raise RuntimeError(f"Eror reading parsha data: {e!r}")

    for chapter in parsha_data["chapters"]:
        for verse in chapter["verses"]:
            verse["text"][metadata.TextSource.HEBREW] = hebrew_text_doc["text"][chapter["chapter"] - 1][verse["verse"] - 1]

    parsha_path(parsha_index).write_text(dump_parsha(parsha_data))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("parsha_index", type=int)
    args = argparser.parse_args()
    parse_hebrew_text(args.parsha_index)
