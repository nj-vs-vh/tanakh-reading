from typing import Any

from aiohttp import web


async def safe_request_json(request: web.Request) -> dict[str, Any]:
    try:
        return await request.json()
    except Exception:
        raise web.HTTPBadRequest(reason="Request body must be a valid JSON")
