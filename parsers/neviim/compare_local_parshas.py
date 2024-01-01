import json
import re
from pathlib import Path

from backend.model import ParshaData
from parsers.merge import merge_parsha_data

CURRENT_DIR = Path(__file__).parent
JSON_DIR = CURRENT_DIR / "../../json/neviim"
PARSHA_JSON_DIRS = [
    (JSON_DIR / dirname).resolve()
    for dirname in [
        "mrk",
        "jps",
        # add sources here; lower in the list = lower priority, checked against all earlier ones
    ]
]

parshas: dict[int, ParshaData] = dict()

for json_dir in PARSHA_JSON_DIRS:
    print(f"Scanning {json_dir}...")
    for file in json_dir.iterdir():
        m = re.match(r".*?(\d+).*\.json", file.name)
        if m is None:
            print(f"Skipping {file}, doesn't look like a parsha file")
            continue
        parsha_id = int(m.group(1))
        print(f"Reading parsha #{parsha_id} from {file}")
        parsha = json.loads(file.read_text())
        current_parsha = parshas.get(parsha_id)
        if current_parsha is None:
            print("Read for the first time, saving")
        else:
            print("Validating and merging")
            parsha = merge_parsha_data(current_parsha, parsha)
        parshas[parsha_id] = parsha
