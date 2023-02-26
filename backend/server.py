import asyncio
import logging
import re
import secrets
from typing import NoReturn, cast

from aiohttp import hdrs, web
from aiohttp.typedefs import Handler
from dictdiffer import diff  # type: ignore

from backend import config, metadata
from backend.auth import generate_signup_token, hash_password
from backend.constants import ACCESS_TOKEN_HEADER, SIGNUP_TOKEN_HEADER, AppExtensions
from backend.database.interface import (
    DatabaseInterface,
    SearchTextIn,
    SearchTextSorting,
)
from backend.model import (
    EditCommentRequest,
    EditTextRequest,
    NewUser,
    ParshaData,
    SignupToken,
    StarCommentRequest,
    StarredComment,
    StoredUser,
    UserCredentials,
)
from backend.utils import (
    iter_parsha_comments,
    safe_request_json,
    worst_language_detection_ever,
)

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


@web.middleware
async def cors_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    try:
        resp = await handler(request)
    except web.HTTPException as e:
        resp = e

    allowed_origins = ["https://torah-reading.surge.sh", "http://torah-reading.surge.sh", "http://localhost:8080"]
    request_origin = request.headers.get(hdrs.ORIGIN)
    logger.debug(f"CORS: request origin = {request_origin}")
    if request_origin is not None:
        origin = request_origin if request_origin in allowed_origins else allowed_origins[0]
        resp.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = origin
        logger.debug(f"CORS: response Access-Control-Allow-Origin set to {origin}")
        resp.headers[
            hdrs.ACCESS_CONTROL_ALLOW_HEADERS
        ] = f"{hdrs.CONTENT_TYPE},{SIGNUP_TOKEN_HEADER},{ACCESS_TOKEN_HEADER}"
        resp.headers[hdrs.ACCESS_CONTROL_ALLOW_METHODS] = "GET,POST,PUT,DELETE,OPTIONS"
        resp.headers[hdrs.ACCESS_CONTROL_MAX_AGE] = "300"

    if isinstance(resp, web.HTTPException):
        raise resp
    else:
        return resp


@routes.options("/{wildcard:.*}")
async def preflight(request: web.Request) -> web.Response:
    # logger.info(f"Request headers: {request.headers}")
    return web.Response()


def get_db(request: web.Request) -> DatabaseInterface:
    return request.app[AppExtensions.DB]


async def get_authorized_user(request: web.Request) -> tuple[StoredUser, str]:
    access_token = request.headers.get(ACCESS_TOKEN_HEADER)
    if access_token is None:
        raise web.HTTPUnauthorized(reason=f"No {ACCESS_TOKEN_HEADER} header found")
    db = get_db(request)
    user = await db.authenticate_user(access_token)
    if user is None:
        raise web.HTTPUnauthorized(reason="Invalid access token, please log in again")
    logger.info(f"Authorized user {user.to_public_json()}")
    return user, access_token


@routes.get("/metadata")
async def get_metadata(request: web.Request) -> web.Response:
    try:
        user, _ = await get_authorized_user(request)
        user_dump = user.to_public_json()
    except Exception:
        user_dump = None

    db = get_db(request)
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
            "commenter_names": metadata.comment_source_names,
            "commenter_links": metadata.comment_source_links,
            "available_parsha": await db.get_available_parsha_indices(),
            "logged_in_user": user_dump,
        }
    )


@routes.get("/parsha/{index}")
async def get_parsha(request: web.Request) -> web.Response:
    parsha_index_str = request.match_info.get("index")
    if parsha_index_str is None:
        raise web.HTTPNotFound(reason="No parsha index in request path")
    try:
        parsha_index = int(parsha_index_str)
    except Exception:
        raise web.HTTPBadRequest(reason="Parsha index must be a number")

    db = get_db(request)
    parsha_data = await db.get_parsha_data(parsha_index)
    if parsha_data is None:
        raise web.HTTPNotFound(reason="Parsha is not available")

    # optional query param things
    add_my_starred_comments_info = request.query.get("my_starred_comments") == "true"
    if add_my_starred_comments_info:
        logger.info(f"Enriching parsha with user-specific data: {add_my_starred_comments_info = }")
        try:
            user, _ = await get_authorized_user(request)

            if add_my_starred_comments_info:
                my_starred_comments = await db.lookup_starred_comments(
                    starrer_username=user.username,
                    parsha=parsha_index,
                )
                my_starred_comment_ids = {str(c.comment_id) for c in my_starred_comments}
                logger.info(f"Marking {len(my_starred_comment_ids)} comment(s) as starred by the user")
                for comment in iter_parsha_comments(parsha_data):
                    if comment["id"] in my_starred_comment_ids:
                        comment["is_starred_by_me"] = True
        except Exception:
            logger.info("Failed to enrich parsha data", exc_info=True)
            pass

    return web.json_response(parsha_data)


@routes.post("/parsha")
async def save_parsha(request: web.Request) -> web.Response:
    if request.headers.get("X-Admin-Token") != config.ADMIN_TOKEN:
        raise web.HTTPUnauthorized(reason="Valid X-Admin-Token required")
    db = get_db(request)
    parsha_data = cast(ParshaData, await safe_request_json(request))
    logger.info(f"Saving parsha data for book {parsha_data['book']}, parsha {parsha_data['parsha']}")
    current_parsha_data = await db.get_parsha_data(parsha_data["parsha"])
    if current_parsha_data is not None:
        logger.info("Current parsha data exists, updating")
        diff_ = list(diff(current_parsha_data, parsha_data))
    else:
        logger.info("No current parsha data, creating new one")
        diff_ = []
    await db.save_parsha_data(parsha_data)
    return web.json_response(diff_)


@routes.put("/text")
async def edit_text(request: web.Request) -> web.Response:
    user, _ = await get_authorized_user(request)
    if not user.is_editor:
        raise web.HTTPUnauthorized(reason="Editor permissions required")
    edit_text_request = EditTextRequest.from_request_json(await safe_request_json(request))
    logger.info(f"Editing text: {edit_text_request}")
    db = get_db(request)
    await db.edit_text(
        text_coords=edit_text_request.text_coords,
        text_source_key=edit_text_request.text_source_key,
        text=edit_text_request.text,
    )
    return web.Response()


@routes.put("/comment")
async def edit_comment(request: web.Request) -> web.Response:
    user, _ = await get_authorized_user(request)
    if not user.is_editor:
        raise web.HTTPUnauthorized(reason="Editor permissions required")
    edit_comment_request = EditCommentRequest.from_request_json(await safe_request_json(request))
    logger.info(f"Editing comment: {edit_comment_request}")
    db = get_db(request)
    await db.edit_comment(
        comment_id=edit_comment_request.comment_id, edited_comment=edit_comment_request.edited_comment
    )
    return web.Response()


@routes.get("/")
async def index(request: web.Request) -> web.Response:
    return web.Response(text="שְׁמַע יִשְׂרָאֵל יְהוָה אֱלֹהֵינוּ יְהוָה אֶחָֽד׃")


async def get_signup_token(request: web.Request) -> SignupToken:
    db = get_db(request)
    signup_token_value = request.headers.get(SIGNUP_TOKEN_HEADER)
    if signup_token_value is None:
        raise web.HTTPUnauthorized(reason=f"No {SIGNUP_TOKEN_HEADER} header found")
    signup_token = await db.lookup_signup_token(signup_token_value)
    if signup_token is None:
        raise web.HTTPUnauthorized(reason="Invalid signup token")
    return signup_token


@routes.get("/check-signup-token")
async def check_signup_token(request: web.Request) -> web.Response:
    await get_signup_token(request)
    return web.Response()


@routes.post("/signup")
async def sign_up(request: web.Request) -> web.Response:
    signup_token = await get_signup_token(request)

    db = get_db(request)
    new_user = NewUser.from_request_json(await safe_request_json(request))
    salt = secrets.token_hex(32)
    new_stored_user = StoredUser(
        data=new_user.data,
        username=new_user.credentials.username,
        invited_by_username=signup_token.creator_username,
        password_hash=hash_password(new_user.credentials.password, salt),
        salt=salt,
    )
    existing_stored_user = await db.lookup_user(new_stored_user.username)
    if existing_stored_user is not None:
        raise web.HTTPConflict(reason="Username already taken")

    created_user = await db.save_user(new_stored_user)
    return web.json_response(created_user.to_public_json())


@routes.post("/login")
async def login(request: web.Request) -> web.Response:
    credentials = UserCredentials.from_request_json(await safe_request_json(request))
    db = get_db(request)
    user = await db.lookup_user(credentials.username)
    if user is None:
        raise web.HTTPNotFound(reason="User not found")
    if hash_password(credentials.password, user.salt) != user.password_hash:
        raise web.HTTPForbidden(reason="Wrong password")
    token = secrets.token_hex(32)
    await db.save_access_token(access_token=token, user=user)
    return web.json_response({"token": token})


@routes.get("/logout")
async def logout(request: web.Request) -> web.Response:
    _, access_token = await get_authorized_user(request)
    db = get_db(request)
    await db.delete_access_token(access_token)
    return web.Response()


@routes.post("/signup-token")
async def new_signup_token(request: web.Request) -> web.Response:
    user, _ = await get_authorized_user(request)
    db = get_db(request)
    existing_token = await db.get_signup_token(creator_username=user.username)
    if existing_token is not None:
        raise web.HTTPForbidden(reason="You can only create one signup token")
    token = await db.save_signup_token(SignupToken(creator_username=user.username, token=generate_signup_token()))
    return web.json_response(token.to_public_json())


@routes.get("/signup-token")
async def get_my_signup_token(request: web.Request) -> web.Response:
    user, _ = await get_authorized_user(request)
    db = get_db(request)
    token = await db.get_signup_token(creator_username=user.username)
    if token is None:
        raise web.HTTPNotFound(reason="You have not yet created a signup token")
    return web.json_response(token.to_public_json())


@routes.post("/starred-comments")
async def star_comment(request: web.Request) -> web.Response:
    user, _ = await get_authorized_user(request)
    star_comment_request = StarCommentRequest.from_request_json(await safe_request_json(request))
    db = get_db(request)
    starred_comment = StarredComment(
        starrer_username=user.username,
        comment_id=star_comment_request.comment_id,
    )
    await db.save_starred_comment(starred_comment)
    # NOTE: using pydantic's .json() here directly because it knows how to serialize PydanticObjectId
    return web.json_response(text=starred_comment.json())


@routes.delete("/starred-comments")
async def unstar_comment(request: web.Request) -> web.Response:
    user, _ = await get_authorized_user(request)
    star_comment_request = StarCommentRequest.from_request_json(await safe_request_json(request))
    db = get_db(request)
    await db.delete_starred_comment(
        StarredComment(
            starrer_username=user.username,
            comment_id=star_comment_request.comment_id,
        )
    )
    return web.Response()


query_peproc_re = re.compile(r"\s+", flags=re.MULTILINE)
MAX_QUERY_LEN = 1024
MIN_QUERY_LEN = 3


@routes.get("/search-text")
async def search_text(request: web.Request) -> web.Response:
    db = get_db(request)
    try:
        query = request.query["query"]
        if len(query) > MAX_QUERY_LEN:
            raise ValueError(f"Query is too long: must be under {MAX_QUERY_LEN} characters")
        query = query_peproc_re.sub(" ", query.strip())
        if len(query) < MIN_QUERY_LEN:
            raise ValueError(f"Query is too short: must be over {MIN_QUERY_LEN} meaningful characters")
        page_size = int(request.query.get("page_size", "50"))
        if not 1 <= page_size <= 100:
            raise ValueError(f"page_size must be between 1 and 100")
        page = int(request.query.get("page", "0"))
        if page < 0:
            raise ValueError(f"page must be positive")

        search_text_results = await db.search_text(
            query=query,
            language=worst_language_detection_ever(query),
            page=page,
            page_size=page_size,
            sorting=SearchTextSorting(request.query.get("sort", SearchTextSorting.START_TO_END.value)),
            search_in=[SearchTextIn(v) for v in request.query.getall("search_in", [sti.value for sti in SearchTextIn])],
            with_verse_parsha_data=bool(request.query.get("with_verse_parsha_data", False)),
        )
    except KeyError as e:
        raise web.HTTPBadRequest(reason=f"Missing required query param: {e}")
    except ValueError as e:
        raise web.HTTPBadRequest(reason=f"Invalid query param: {e}")
    return web.json_response(search_text_results.to_public_json())


async def start_background_jobs(app: web.Application) -> None:
    background_jobs = set[asyncio.Task[NoReturn]]()

    async def monitor_parsha_cache() -> NoReturn:
        logger.info("Running parsha cache monitoring")
        db: DatabaseInterface = app[AppExtensions.DB]
        while True:
            logger.info(f"Cached parsha indices: {await db.get_cached_parsha_indices()}")
            await asyncio.sleep(60 * 60)

    background_jobs.add(asyncio.create_task(monitor_parsha_cache()))
    app[AppExtensions.BACKGROUND_JOBS_SET] = background_jobs  # to prevent garbage collection


class BackendApp:
    def __init__(self, db: DatabaseInterface) -> None:
        self.db = db
        self.app = web.Application(client_max_size=10 * 1024**2)
        self.app.middlewares.append(cors_middleware)
        self.app.add_routes(routes)
        self.app[AppExtensions.DB] = db

        async def db_setup(app: web.Application):
            logger.info(f"Setting up db: {db}")
            await db.setup()

        self.app.on_startup.append(db_setup)
        self.app.on_startup.append(start_background_jobs)

    def run(self) -> None:
        web.run_app(self.app, port=config.PORT, access_log=logger if not config.IS_PROD else None)
