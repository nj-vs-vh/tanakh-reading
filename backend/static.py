import logging
from pathlib import Path

from aiohttp import web
from aiohttp.typedefs import Handler

from backend.config import STATIC_DIR

logger = logging.getLogger(__name__)


def static_dir() -> Path:
    if STATIC_DIR is None:
        raise web.HTTPUnprocessableEntity(reason="Directory for static files is not configured")
    else:
        return Path(STATIC_DIR)


def setup_frontend_routes(routes: web.RouteTableDef) -> None:
    @routes.get("/frontend{wildcard:.*}")
    async def serve_spa(request: web.Request) -> web.Response:
        return web.Response(
            body=(static_dir() / "index.html").read_bytes(),
            content_type="text/html",
        )

    ALLOWED_PATHS = [
        ("global.css", "text/css"),
        ("build/bundle.css", "text/css"),
        ("build/bundle.js", "*/*"),
        ("build/bundle.js.map", "*/*"),
        ("favicon.png", "*/*"),
    ]

    def get_handler(allowed_path: str, mime_type: str) -> Handler:
        async def handler(_: web.Request) -> web.Response:
            logger.info(f"Serving allowed path: {allowed_path!r}")
            return web.Response(
                body=(static_dir() / allowed_path).read_bytes(),
                content_type=mime_type,
            )

        return handler

    for allowed_path, mime_type in ALLOWED_PATHS:
        routes.get("/" + allowed_path)(get_handler(allowed_path, mime_type))
