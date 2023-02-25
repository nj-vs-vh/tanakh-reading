import json
from pathlib import Path

import pytest

from backend.database.mongo import (
    parsha_data_to_texts_and_comments,
    texts_and_comments_to_parsha_data,
)

JSON_DIR = Path(__file__).parent.parent / "json"
PARSHA_DATA_JSON_PATHS = [p for p in JSON_DIR.iterdir() if p.stem.isdigit() and p.suffix == ".json"]


@pytest.mark.parametrize("parsha_data_path", PARSHA_DATA_JSON_PATHS)
def test_parsha_data_storage(parsha_data_path: Path):
    parsha_data = json.loads(parsha_data_path.read_text())
    texts, comments = parsha_data_to_texts_and_comments(parsha_data)
    parsha_data_restored = texts_and_comments_to_parsha_data(texts, comments)
    assert parsha_data == parsha_data_restored
