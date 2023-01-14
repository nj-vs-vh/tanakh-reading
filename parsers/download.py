import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import List, Optional

import aiohttp


async def main(index: int, output_path: Path):
    print(f"Downloading parsha {index}")
    async with aiohttp.ClientSession() as session:
        response = await session.get(f"{os.environ['BASE_URL']}/parsha/{index}")
        print(f"Response status: {response.status}")
        if response.status != 200:
            print(f"Can't get parsha {index}: {await response.text()}")
        else:
            response_json = await response.json()
            print(f"Writing {output_path}")
            output_path.write_text(json.dumps(response_json, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("parsha_indices", type=str, nargs="+")
    argparser.add_argument("--override", action="store_true")
    args = argparser.parse_args()

    indices_str = args.parsha_indices
    indices_with_placeholders: List[Optional[int]] = []

    for ind_str in indices_str:
        try:
            index = int(ind_str)
            indices_with_placeholders.append(index)
        except Exception:
            if ind_str == "-":
                indices_with_placeholders.append(None)
            else:
                print(f"Bad argument: {ind_str}")

    indices_set = {i for i in indices_with_placeholders if i is not None}
    for argidx, index_or_placeholder in enumerate(indices_with_placeholders):
        if index_or_placeholder is None:
            lower = (indices_with_placeholders[argidx - 1] if argidx > 0 else 1) or 1
            upper = (indices_with_placeholders[argidx + 1] if argidx < len(indices_with_placeholders) - 1 else 54) or 54
            indices_set.update(range(lower, upper + 1))

    indices = sorted(indices_set)

    print(f"Downloading parshas from {os.environ['BASE_URL']}: ", indices)

    for index in indices:
        output_path = Path(f"json/{index}.json")
        if not args.override and output_path.exists():
            print(f"File already exists and override flag is not set, ignoring: {output_path}")
            continue
        asyncio.run(main(index, output_path))
