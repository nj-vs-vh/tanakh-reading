import json
import logging
from pathlib import Path
from typing import Optional

from backend.model import ParshaData

logger = logging.getLogger(__name__)


JSON_DIR = (Path(__file__).parent / "../json").resolve()


def parsha_path(parsha: int) -> Path:
    return JSON_DIR / f"{parsha}.json"


def get_parsha_data(parsha: int) -> Optional[ParshaData]:
    path = parsha_path(parsha)
    if not path.exists():
        return None
    logger.info(f"Reading parsha #{parsha} from {path}")
    return json.loads(path.read_text())
