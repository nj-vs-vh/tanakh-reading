import hashlib
import logging
from pathlib import Path

from aiohttp import hdrs, web
from aiohttp.typedefs import Handler

import config
import metadata

routes = web.RouteTableDef()

logger = logging.getLogger(__name__)


PASSWORD = "torah-reading"
PASSWORD_HASH = hashlib.sha256(PASSWORD.encode()).hexdigest()[:32]

JSON_DIR = Path("json")


@web.middleware
async def auth_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    if request.headers.get("X-Password-Hash", "") != PASSWORD_HASH:
        raise web.HTTPUnauthorized()
    return await handler(request)


@web.middleware
async def cors_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    resp = await handler(request)
    allowed_origins = ["https://torah-reading.surge.sh", "http://torah-reading.surge.sh", "http://localhost:8080"]
    request_origin = request.headers.get(hdrs.ORIGIN)
    if request_origin is not None:
        origin = request_origin if request_origin in allowed_origins else allowed_origins[0]
        resp.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = origin
        resp.headers[hdrs.ACCESS_CONTROL_ALLOW_HEADERS] = str(hdrs.CONTENT_TYPE)
        resp.headers[hdrs.ACCESS_CONTROL_ALLOW_METHODS] = "POST, GET, OPTIONS"
        resp.headers[hdrs.ACCESS_CONTROL_MAX_AGE] = "300"
    return resp


@routes.options("/{wildcard:.*}")
async def preflight(request: web.Request) -> web.Response:
    # logger.info(f"Request headers: {request.headers}")
    return web.Response()


@routes.get("/metadata")
async def get_metadata(request: web.Request) -> web.Response:
    available_parsha = sorted(int(json_file.stem) for json_file in JSON_DIR.iterdir())
    return web.json_response(
        {
            "book_names": metadata.torah_book_names,
            "parsha_ranges": metadata.torah_book_parsha_ranges,
            "chapter_verse_ranges": metadata.chapter_verse_ranges,
            "parsha_names": metadata.parsha_names,
            "text_sources": metadata.TextSource.all(),
            "text_source_marks": metadata.text_source_marks,
            "text_source_descriptions": metadata.text_source_descriptions,
            "text_source_links": metadata.text_source_links,
            "commenter_names": metadata.commenter_names,
            "commenter_links": metadata.commenter_links,
            "available_parsha": available_parsha,
        }
    )


@routes.get("/parsha/{index}")
async def get_parsha(request: web.Request):
    parsha_index = request.match_info.get("index")
    if parsha_index is None:
        raise web.HTTPNotFound(reason="No parsha index in request")
    parsha_file = JSON_DIR / f"{parsha_index}.json"
    if not parsha_file.exists():
        raise web.HTTPNotFound(reason="No parsha available with such index")
    return web.json_response(text=parsha_file.read_text())


@routes.get("/")
async def index(request: web.Request):
    return web.Response(text="שְׁמַע יִשְׂרָאֵל יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָֽד׃")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s")
    app = web.Application(client_max_size=1024)
    app.middlewares.append(cors_middleware)
    app.add_routes(routes)
    web.run_app(app, port=config.PORT)
