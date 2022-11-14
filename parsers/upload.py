import argparse
import asyncio
import json
import os
from pprint import pprint

import aiohttp

from parsers.local_storage import parsha_path


async def main(index: int):
    parsha_data = json.loads(parsha_path(index).read_text())
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            f"{os.environ['BASE_URL']}/parsha",
            json=parsha_data,
            headers={"X-Admin-Token": os.environ["ADMIN_TOKEN"]},
        )
        print(f"Response status: {response.status}")
        response_json = await response.json()
        pprint(response_json)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("parsha_index", type=int)
    args = argparser.parse_args()
    asyncio.run(main(args.parsha_index))
