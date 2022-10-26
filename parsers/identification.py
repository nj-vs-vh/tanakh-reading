from uuid import uuid4

from backend.model import ParshaData


def ensure_comment_ids(parsha_data: ParshaData):
    for chapter in parsha_data["chapters"]:
        for verse in chapter["verses"]:
            for _, comments in verse["comments"].items():
                for comment in comments:
                    if "id" not in comment:
                        comment["id"] = str(uuid4())
