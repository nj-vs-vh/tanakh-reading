import asyncio
import datetime
import json
import logging
import re
import secrets
from typing import NoReturn, Optional, cast

import bson
from aiohttp import hdrs, web
from aiohttp.typedefs import Handler
from dictdiffer import diff  # type: ignore

from backend import config
from backend.auth import generate_signup_token, hash_password
from backend.constants import ACCESS_TOKEN_HEADER, SIGNUP_TOKEN_HEADER, AppExtensions
from backend.database.interface import (
    DatabaseInterface,
    SearchTextIn,
    SearchTextSorting,
)
from backend.metadata.neviim import NEVIIM_METADATA
from backend.metadata.torah import TORAH_METADATA
from backend.model import (
    DisplayedUserComment,
    EditCommentRequest,
    EditTextRequest,
    NewUser,
    ParshaData,
    ParshaDataModel,
    SignupToken,
    StarCommentRequest,
    StarredComment,
    StarredCommentLookupResponse,
    StarredCommentMetaResponse,
    StoredUser,
    StoredUserComment,
    TextOrCommentIterRequest,
    UserCommentPayload,
    UserCredentials,
)
from backend.utils import safe_request_json, worst_language_detection_ever

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()


@web.middleware
async def cors_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    try:
        resp = await handler(request)
    except web.HTTPException as e:
        resp = e

    allowed_origins = [
        "https://torah-reading-jnn6c.kinsta.page",
        "http://torah-reading-jnn6c.kinsta.page",
        "https://torah-reading.surge.sh",
        "http://torah-reading.surge.sh",
        "http://localhost:8080",
    ]
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


async def get_authorized_user(request: web.Request, require_editor: bool = False) -> tuple[StoredUser, str]:
    access_token = request.headers.get(ACCESS_TOKEN_HEADER)
    if access_token is None:
        raise web.HTTPUnauthorized(reason=f"No {ACCESS_TOKEN_HEADER} header found")
    db = get_db(request)
    user = await db.authenticate_user(access_token)
    if user is None:
        raise web.HTTPUnauthorized(reason="Invalid access token, please log in again")
    logger.info(f"Authorized user {user.to_public_json()}")
    if require_editor and not user.is_editor:
        raise web.HTTPUnauthorized(reason="Editor permissions required")
    return user, access_token


@routes.get("/metadata")
async def get_metadata(request: web.Request) -> web.Response:
    try:
        user, _ = await get_authorized_user(request)
        user_json = json.loads(user.to_public_json())
    except Exception:
        user_json = None

    db = get_db(request)
    return web.json_response(
        {
            "sections": {
                "torah": TORAH_METADATA.dict(),
                "neviim": NEVIIM_METADATA.dict(),
            },
            "available_parsha": await db.get_available_parsha_indices(),
            "logged_in_user": user_json,
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
    add_my_starred_comments = request.query.get("my_starred_comments")
    add_user_comments = request.query.get("add_user_comments")
    if any(query_param is not None for query_param in (add_my_starred_comments, add_user_comments)):
        logger.info(f"Adding user-specific data to parsha: {add_my_starred_comments = } {add_user_comments = }")
        try:
            user, _ = await get_authorized_user(request)

            starred_comment_ids = set[str]()
            if add_my_starred_comments == "true":
                starred_comment_ids = {
                    str(c.comment_id)
                    for c in await db.lookup_starred_comments(
                        starrer_username=user.username,
                        parsha=parsha_index,
                    )
                }
                logger.info(f"Found {len(starred_comment_ids)} starred comment(s)")

            user_comments: list[DisplayedUserComment] = []
            if add_user_comments == "mine":
                user_comments = await db.lookup_user_comments(username=user.username, parsha=parsha_index)

            # inserting the stuff we found into the parsha data
            for chapter in parsha_data["chapters"]:
                chapter_user_comments = [uc for uc in user_comments if uc.text_coords.chapter == chapter["chapter"]]
                for verse in chapter["verses"]:
                    verse["user_comments"] = [
                        # HACK: this is TERRIBLE but I am not going to fix it until a proper refactoring!!! sorry!!!!!!
                        json.loads(uc.json())  # type: ignore
                        for uc in chapter_user_comments
                        if uc.text_coords.verse == verse["verse"]
                    ]
                    for _, comments in verse["comments"].items():
                        for comment in comments:
                            if comment["id"] in starred_comment_ids:
                                comment["is_starred_by_me"] = True
        except Exception:
            logger.info("Failed to add user-specific data to parsha, will return without it", exc_info=True)

    return web.json_response(parsha_data)


def check_admin_token(request: web.Request) -> None:
    if request.headers.get("X-Admin-Token") != config.ADMIN_TOKEN:
        raise web.HTTPUnauthorized(reason="Valid X-Admin-Token required")


@routes.post("/parsha")
async def save_parsha_data(request: web.Request) -> web.Response:
    """Upload a whole new parsha, replacing all currently existing data for it"""
    check_admin_token(request)
    db = get_db(request)
    parsha_data = cast(ParshaData, await safe_request_json(request))
    try:
        ParshaDataModel(**parsha_data)
    except Exception as e:
        raise web.HTTPBadRequest(reason=repr(e))
    logger.info(f"Saving parsha data for book {parsha_data['book']}, parsha {parsha_data['parsha']}")
    current_parsha_data = await db.get_parsha_data(parsha_data["parsha"])
    if current_parsha_data is not None:
        logger.info("Current parsha data exists, will overwrite")
        diff_ = list(diff(current_parsha_data, parsha_data))
    else:
        logger.info("No current parsha data, creating new one")
        diff_ = []
    await db.save_parsha_data(parsha_data, replace=True)
    return web.json_response(diff_)


@routes.put("/parsha")
async def append_parsha_data(request: web.Request) -> web.Response:
    """Upload data in form of a Parsha object, but not remove already existing data"""
    check_admin_token(request)
    db = get_db(request)
    parsha_data = cast(ParshaData, await safe_request_json(request))
    try:
        ParshaDataModel(**parsha_data)
    except Exception as e:
        raise web.HTTPBadRequest(reason=repr(e))
    logger.info(f"Appending data from parsha data object (book {parsha_data['book']}, parsha {parsha_data['parsha']})")
    await db.save_parsha_data(parsha_data, replace=False)
    return web.Response()


@routes.delete("/parsha-cache")
async def invalidate_parsha_cache(request: web.Request) -> web.Response:
    check_admin_token(request)
    await get_db(request).drop_parsha_cache()
    return web.Response()


@routes.put("/text")
async def edit_text(request: web.Request) -> web.Response:
    await get_authorized_user(request, require_editor=True)
    edit_text_request = EditTextRequest.from_request_json(await safe_request_json(request))
    logger.info(f"Editing text: {edit_text_request}")
    db = get_db(request)
    await db.edit_text(
        text_id=edit_text_request.id,
        text=edit_text_request.text,
    )
    return web.Response()


@routes.put("/comment")
async def edit_comment(request: web.Request) -> web.Response:
    await get_authorized_user(request, require_editor=True)
    edit_comment_request = EditCommentRequest.from_request_json(await safe_request_json(request))
    logger.info(f"Editing comment: {edit_comment_request}")
    db = get_db(request)
    await db.edit_comment(
        comment_id=edit_comment_request.comment_id, edited_comment=edit_comment_request.edited_comment
    )
    return web.Response()


@routes.get("/")
async def index(request: web.Request) -> web.Response:
    return web.Response(text="hello")


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
    return web.json_response(text=created_user.to_public_json())


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
    return web.json_response(text=token.to_public_json())


@routes.get("/signup-token")
async def get_my_signup_token(request: web.Request) -> web.Response:
    user, _ = await get_authorized_user(request)
    db = get_db(request)
    token = await db.get_signup_token(creator_username=user.username)
    if token is None:
        raise web.HTTPNotFound(reason="You have not yet created a signup token")
    return web.json_response(text=token.to_public_json())


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


@routes.get("/starred-comments-meta")
async def get_starred_comments_meta(request: web.Request) -> web.Response:
    user, _ = await get_authorized_user(request)
    db = get_db(request)
    total_by_parsha = await db.count_starred_comments_by_parsha(user.username)
    total = sum(total_by_parsha.values()) or 0
    logger.info(f"Starred comments meta: {total_by_parsha = } {total = }")
    return web.json_response(
        text=StarredCommentMetaResponse(
            total=total,
            total_by_parsha=total_by_parsha,
            random_starred_comment_data=await db.load_random_starred_comment_data(user.username),
        ).to_public_json()
    )


def _get_pagination_query_params(request: web.Request) -> tuple[int, int]:
    try:
        page_size = int(request.query.get("page_size", "50"))
        if not 1 <= page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")
        page = int(request.query.get("page", "0"))
        if page < 0:
            raise ValueError("page must be non-negative")
        return page_size, page
    except Exception as e:
        raise web.HTTPBadRequest(reason=f"Invalid pagination query param: {e}")


@routes.get("/starred-comments")
async def get_starred_comments(request: web.Request) -> web.Response:
    user, _ = await get_authorized_user(request)

    parsha_indices_str = request.query.get("parsha_indices", "")
    try:
        if parsha_indices_str:
            parsha_indices = [int(p.strip()) for p in parsha_indices_str.split(",")]
        else:
            parsha_indices = []
    except Exception:
        raise web.HTTPBadRequest(reason="parsha_indices query param must be a comma-separated list of integers")

    page_size, page = _get_pagination_query_params(request)

    logger.info(f"Looking up starred comments with {parsha_indices = } {page = } {page_size = }")

    db = get_db(request)
    return web.json_response(
        text=StarredCommentLookupResponse(
            starred_comments=await db.lookup_starred_comments_data(
                starrer_username=user.username, parsha_indices=parsha_indices, page=page, page_size=page_size
            )
        ).to_public_json()
    )


query_peproc_re = re.compile(r"\s+", flags=re.MULTILINE)
MAX_QUERY_LEN = 1024
MIN_QUERY_LEN = 3


@routes.get("/search-text")
async def search_text(request: web.Request) -> web.Response:
    try:
        user, _ = await get_authorized_user(request)
        username: Optional[str] = user.username
    except Exception:
        username = None

    db = get_db(request)
    try:
        query = request.query["query"]
        if len(query) > MAX_QUERY_LEN:
            raise ValueError(f"Query is too long: must be under {MAX_QUERY_LEN} characters")
        query = query_peproc_re.sub(" ", query.strip())
        if len(query) < MIN_QUERY_LEN:
            raise ValueError(f"Query is too short: must be over {MIN_QUERY_LEN} meaningful characters")
        page_size, page = _get_pagination_query_params(request)
        search_text_results = await db.search_text(
            query=query,
            language=worst_language_detection_ever(query),
            page=page,
            page_size=page_size,
            sorting=SearchTextSorting(request.query.get("sorting", SearchTextSorting.START_TO_END.value)),
            search_in=[SearchTextIn(v) for v in request.query.getall("search_in", [sti.value for sti in SearchTextIn])],
            with_verse_parsha_data=bool(request.query.get("with_verse_parsha_data", False)),
            username=username,
        )
    except KeyError as e:
        raise web.HTTPBadRequest(reason=f"Missing required query param: {e}")
    except ValueError as e:
        raise web.HTTPBadRequest(reason=f"Invalid query param: {e}")
    return web.json_response(text=search_text_results.to_public_json())


@routes.post("/count/comments")
async def count_comments(request: web.Request) -> web.Response:
    await get_authorized_user(request, require_editor=True)
    db = get_db(request)
    parsed = TextOrCommentIterRequest.from_request_json(await safe_request_json(request))
    return web.json_response({"count": await db.count_comments(parsed)})


@routes.post("/count/texts")
async def count_texts(request: web.Request) -> web.Response:
    await get_authorized_user(request, require_editor=True)
    db = get_db(request)
    parsed = TextOrCommentIterRequest.from_request_json(await safe_request_json(request))
    return web.json_response({"count": await db.count_texts(parsed)})


@routes.post("/iter/comments")
async def iter_comments(request: web.Request) -> web.Response:
    await get_authorized_user(request, require_editor=True)
    db = get_db(request)
    parsed = TextOrCommentIterRequest.from_request_json(await safe_request_json(request))
    next_comment = await db.iter_comments(parsed)
    if next_comment is None:
        raise web.HTTPNotFound()
    else:
        return web.json_response(text=next_comment.to_public_json())


@routes.post("/iter/texts")
async def iter_texts(request: web.Request) -> web.Response:
    await get_authorized_user(request, require_editor=True)
    db = get_db(request)
    parsed = TextOrCommentIterRequest.from_request_json(await safe_request_json(request))
    next_text = await db.iter_texts(parsed)
    if next_text is None:
        raise web.HTTPNotFound()
    else:
        return web.json_response(text=next_text.to_public_json())


@routes.post("/user-comment")
async def create_user_comment(request: web.Request) -> web.Response:
    user, _ = await get_authorized_user(request)
    db = get_db(request)
    payload = UserCommentPayload.from_request_json(await safe_request_json(request))
    comment = await db.save_user_comment(
        StoredUserComment(
            text_coords=payload.text_coords,
            anchor_phrase=payload.anchor_phrase,
            comment=payload.comment,
            author_username=user.username,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
    )
    return web.json_response(text=comment.to_public_json())


@routes.delete("/user-comment/{comment_id}")
async def delete_user_comment(request: web.Request) -> web.Response:
    user, _ = await get_authorized_user(request)
    db = get_db(request)

    comment_id_str = request.match_info.get("comment_id")
    if comment_id_str is None:
        raise web.HTTPNotFound(reason="No comment id in request path")
    try:
        comment_id = bson.ObjectId(comment_id_str)
    except Exception:
        raise web.HTTPBadRequest(reason="Invalid comment id")

    is_deleted = await db.delete_user_comment(comment_id, author_username=user.username)
    if is_deleted:
        raise web.HTTPNoContent(reason="Comment deleted")
    else:
        raise web.HTTPNotFound(reason="Comment not found")


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
