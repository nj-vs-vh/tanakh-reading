import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

from backend.model import ParshaData

logger = logging.getLogger(__name__)


JSON_DIR = (Path(__file__).parent / "../json").resolve()


def parsha_path(parsha: int) -> Path:
    return JSON_DIR / f"{parsha}.json"


@lru_cache(maxsize=None)
def get_parsha_data(parsha: int) -> Optional[ParshaData]:
    path = parsha_path(parsha)
    if not path.exists():
        return None
    logger.info(f"Reading parsha #{parsha} from {path}")
    return json.loads(path.read_text())


@lru_cache(maxsize=None)
def get_available_parsha() -> list[int]:
    result = sorted(int(json_file.stem) for json_file in JSON_DIR.iterdir())
    logger.info(f"List of available parshas: {result}")
    return result
