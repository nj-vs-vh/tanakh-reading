import argparse
import json
from pathlib import Path

from backend.model import ParshaData
from parsers.utils import postprocess_patched_text

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("input", type=str)
    argparser.add_argument("output", type=str)
    args = argparser.parse_args()

    output_path = Path(args.output)
    # if output_path.exists():
    #     raise FileExistsError(f"Output file exists: {output_path.absolute()}")

    input_path = Path(args.input)
    parsha_data: ParshaData = json.loads(input_path.read_text())

    for chapter in parsha_data["chapters"]:
        for verse in chapter["verses"]:
            if "rashi" not in verse["comments"]:
                continue
            for rashi_comment in verse["comments"]["rashi"]:
                rashi_comment["comment"] = postprocess_patched_text(rashi_comment["comment"])

    output_path.write_text(json.dumps(parsha_data, indent=2, ensure_ascii=False))
