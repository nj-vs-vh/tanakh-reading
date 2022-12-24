import argparse
import asyncio
import json
import os
from pathlib import Path

import aiohttp


async def main(index: int, output_path: Path):
    async with aiohttp.ClientSession() as session:
        response = await session.get(f"{os.environ['BASE_URL']}/parsha/{index}")
        print(f"Response status: {response.status}")
        response_json = await response.json()
        output_path.write_text(json.dumps(response_json, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("parsha_index", type=int)
    argparser.add_argument("--output_path", type=str, default='', required=False)
    argparser.add_argument("--override", action="store_true")
    args = argparser.parse_args()

    output_path = Path(args.output_path or f'json/{args.parsha_index}.json')
    if output_path.exists() and not args.override:
        raise FileExistsError(f"Output file exists: {output_path.absolute()}")

    asyncio.run(main(args.parsha_index, output_path))
