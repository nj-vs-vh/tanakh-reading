from pathlib import Path

JSON_DIR = (Path(__file__).parent / "../json").resolve()


def parsha_json(parsha: int) -> Path:
    return JSON_DIR / f"{parsha}.json"


def available_parsha() -> list[int]:
    return sorted(int(json_file.stem) for json_file in JSON_DIR.iterdir())
