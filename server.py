import hashlib
from pathlib import Path
from aiohttp import web, hdrs
from aiohttp.typedefs import Handler

import metadata
import config


routes = web.RouteTableDef()


PASSWORD = "torah-reading"
PASSWORD_HASH = hashlib.sha256(PASSWORD.encode()).hexdigest()[:32]

JSON_DIR = Path("json")


@web.middleware
async def auth_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    if request.headers.get('X-Password-Hash', '') != PASSWORD_HASH:
        raise web.HTTPUnauthorized()
    return await handler(request)


@web.middleware
async def cors_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    resp = await handler(request)
    allowed_origin = "https://torah-reading.surge.sh" if config.IS_PROD else "http://localhost:8080"
    resp.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = allowed_origin
    resp.headers[hdrs.ACCESS_CONTROL_ALLOW_HEADERS] = "Content-Type"
    resp.headers[hdrs.ACCESS_CONTROL_ALLOW_METHODS] = "POST, GET, OPTIONS"
    return resp


@routes.options("/{wildcard:.*}")
async def preflight(request: web.Request) -> web.Response:
    return web.Response()


@routes.get("/metadata")
async def get_metadata(request: web.Request) -> web.Response:
    available_parsha = sorted(int(json_file.stem) for json_file in JSON_DIR.iterdir())
    return web.json_response(
        {
            "book_names": metadata.torah_book_names,
            "parsha_ranges": metadata.torah_book_parsha_ranges,
            "parsha_names": metadata.parsha_names,
            "translation_about_links": metadata.translation_about_url,
            "translation_names": {
                metadata.Translation.FG: "Перевод Фримы Гурфинкель"
            },
            "commenter_about_links": metadata.commenter_about_url,
            "commenter_names": {
                metadata.Commenter.SONCHINO: "Сончино",
                metadata.Commenter.RASHI: "Раши",
            },
            "available_parsha": available_parsha,
        }
    )


@routes.get("/parsha/{index}")
async def get_parsha(request: web.Request):
    parsha_index = request.match_info.get('index')
    if parsha_index is None:
        raise web.HTTPNotFound(reason='No parsha index in request')
    parsha_file = JSON_DIR / f'{parsha_index}.json'
    if not parsha_file.exists():
        raise web.HTTPNotFound(reason='No parsha available with such index')
    return web.json_response(text=parsha_file.read_text())


@routes.get("/")
async def index(request: web.Request):
    return web.Response(text="שְׁמַע יִשְׂרָאֵל יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָֽד׃")


if __name__ == "__main__":
    app = web.Application(client_max_size=1024)
    app.middlewares.append(cors_middleware)
    app.add_routes(routes)
    web.run_app(app, port=config.PORT)
