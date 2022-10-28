from uuid import uuid4

from backend.model import ParshaData
from backend.utils import iter_parsha_comments


def ensure_comment_ids(parsha_data: ParshaData) -> None:
    for comment_data in iter_parsha_comments(parsha_data):
        if "id" not in comment_data:
            comment_data["id"] = str(uuid4())
