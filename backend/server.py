import logging
import secrets
from hashlib import sha256
from typing import Awaitable, Callable

from aiohttp import hdrs, web
from aiohttp.typedefs import Handler

from backend import config, metadata
from backend.auth import hash_password
from backend.constants import AppExtensions
from backend.database.interface import DatabaseInterface
from backend.model import StoredUser, SubmittedUserCredentials
from backend.static import available_parsha, parsha_json
from backend.utils import safe_request_json

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


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
            "available_parsha": available_parsha(),
        }
    )


@routes.get("/parsha/{index}")
async def get_parsha(request: web.Request) -> web.Response:
    parsha_index_str = request.match_info.get("index")
    if parsha_index_str is None:
        raise web.HTTPNotFound(reason="No parsha index in request")

    try:
        parsha_index = int(parsha_index_str)
    except Exception:
        raise web.HTTPBadRequest(reason="Parsha index must be a number")

    parsha_file = parsha_json(parsha_index)
    if not parsha_file.exists():
        raise web.HTTPNotFound(reason="No parsha available with such index")
    return web.json_response(text=parsha_file.read_text())


@routes.get("/")
async def index(request: web.Request) -> web.Response:
    return web.Response(text="שְׁמַע יִשְׂרָאֵל יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָֽד׃")


def get_db(request: web.Request) -> DatabaseInterface:
    return request.app[AppExtensions.DB]


@routes.post("/signup")
async def sign_up(request: web.Request) -> web.Response:
    db = get_db(request)

    signup_token_value = request.headers.get('X-Signup-Token')
    if signup_token_value is None:
        raise web.HTTPUnauthorized(reason="No signup token found in X-Signup-Token header")
    
    signup_token = await db.lookup_signup_token(signup_token_value)
    if signup_token is None:
        raise web.HTTPUnauthorized(reason="Signup token is invalid")

    new_user_credentials = SubmittedUserCredentials.from_user_data(await safe_request_json(request))
    salt = secrets.token_hex(32)
    potential_new_user = StoredUser(
        username=new_user_credentials.username,
        invited_by_username=signup_token.creator_username,
        password_hash=hash_password(new_user_credentials.password, salt),
        salt=salt,
    )
    existing_user = await db.lookup_user(potential_new_user.username)
    if existing_user is not None:
        raise web.HTTPConflict(reason="User with this username already exists")

    created_user = await db.save_user(potential_new_user)
    return web.json_response(created_user.dict_public())


@routes.post("/login")
async def login(request: web.Request) -> web.Response:
    credentials = SubmittedUserCredentials.from_user_data(await safe_request_json(request))
    db = get_db(request)
    user = await db.lookup_user(credentials.username)
    if user is None:
        raise web.HTTPNotFound(reason="User with this username not found")
    if hash_password(credentials.password, user.salt) != user.password_hash:
        raise web.HTTPForbidden(reason="Wrong password")
    return web.json_response(user.dict_public())


class BackendApp:
    def __init__(self, db: DatabaseInterface) -> None:
        self.db = db
        self.app = web.Application(client_max_size=1024)
        self.app.middlewares.append(cors_middleware)
        self.app.add_routes(routes)
        self.app[AppExtensions.DB] = db

        async def db_setup(app: web.Application):
            await db.setup()

        self.app.on_startup.append(db_setup)

    def run(self) -> None:
        web.run_app(self.app, port=config.PORT)
