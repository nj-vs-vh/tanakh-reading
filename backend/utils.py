from typing import Any, Generator

from aiohttp import web

from backend.model import CommentData, ParshaData


async def safe_request_json(request: web.Request) -> dict[str, Any]:
    try:
        return await request.json()
    except Exception:
        raise web.HTTPBadRequest(reason="Request body must be a valid JSON")


def iter_parsha_comments(parsha_data: ParshaData) -> Generator[CommentData, None, None]:
    for chapter in parsha_data["chapters"]:
        for verse in chapter["verses"]:
            for _, comments in verse["comments"].items():
                for comment in comments:
                    yield comment
