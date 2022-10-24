import copy
import json

from backend.model import ParshaData
from backend.static import parsha_json


def merge_parsha_data(p1: ParshaData, p2: ParshaData) -> ParshaData:
    result = copy.deepcopy(p1)

    if result["book"] != p2["book"]:
        raise ValueError(f"Only parshas of the same book can be merged, but {result['book']} != {p2['book']}")
    if result["parsha"] != p2["parsha"]:
        raise ValueError(f"Only parshas with the same number can be merged, but {result['parsha']} != {p2['parsha']}")

    chapters_1 = [ch["chapter"] for ch in result["chapters"]]
    chapters_2 = [ch["chapter"] for ch in p2["chapters"]]
    if chapters_1 != chapters_2:
        raise ValueError(f"Parshas have different chapters: {chapters_1} (existing) and {chapters_2} (new)")

    for ch1, ch2 in zip(result["chapters"], p2["chapters"]):
        verses_1 = [v["verse"] for v in ch1["verses"]]
        verses_2 = [v["verse"] for v in ch2["verses"]]
        if verses_1 != verses_2:
            raise ValueError(
                f"Chapter {ch1['chapter']} has different verses: {verses_1} (existing) and {verses_2} (new)"
            )
        for v1, v2 in zip(ch1["verses"], ch2["verses"]):
            text_sources_1 = set(v1["text"].keys())
            text_sources_2 = set(v2["text"].keys())
            text_source_intersection = text_sources_1 & text_sources_2
            if text_source_intersection:
                raise ValueError(
                    f"{ch1['chapter']}:{v1['verse']} is set in both inputs for sources: {text_source_intersection}"
                )
            v1["text"].update(v2["text"])

            for commenter, comments in v2["comments"].items():
                if commenter in v1["comments"]:
                    v1["comments"][commenter].extend(comments)
                else:
                    v1["comments"][commenter] = comments

    return result


def merge_and_save_parsha_data(parsha: int, new_parsha_data: ParshaData):
    existing_parsha_data = json.loads(parsha_json(parsha).read_text())
    resulting_parsha_data = merge_parsha_data(existing_parsha_data, new_parsha_data)
    parsha_json(parsha).write_text(json.dumps(resulting_parsha_data, ensure_ascii=False, indent=2))
