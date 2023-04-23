import { withAccessTokenHeader } from "./auth";
import { isProduction } from "./config";
import type { ParshaData, Metadata, SignupData, UserCredentials, SingleText, SingleComment } from "./types";


// @ts-ignore
const BASE_API_URL = isProduction ? "https://torah-reading-backend.herokuapp.com" : "http://localhost:8081";


export async function getParsha(index: number, withUserData: boolean): Promise<ParshaData> {
    let url = `${BASE_API_URL}/parsha/${index}`;
    if (withUserData) {
        const queryParams = new URLSearchParams({
            my_starred_comments: "true",
        })
        url = url + "?" + queryParams.toString()
    }

    const resp = await fetch(
        url,
        { headers: withAccessTokenHeader({ 'Content-Type': 'application/json' }) }
    )
    const respText = await resp.text();
    if (resp.ok)
        return JSON.parse(respText);
    else
        throw (respText);
}


export async function getMetadata(): Promise<Metadata> {
    const resp = await fetch(
        `${BASE_API_URL}/metadata`,
        { headers: withAccessTokenHeader({ 'Content-Type': 'application/json' }) }
    )
    const respText = await resp.text();

    if (resp.ok) {
        return JSON.parse(respText);
    } else {
        throw respText;
    }
}


export async function checkSignupToken(token: string): Promise<boolean> {
    const resp = await fetch(
        `${BASE_API_URL}/check-signup-token`,
        { headers: { 'Content-Type': 'application/json', 'X-Signup-Token': token } }
    )
    return resp.ok;
}


export async function signup(token: string, data: SignupData): Promise<null> {
    const resp = await fetch(
        `${BASE_API_URL}/signup`,
        {
            method: "POST",
            headers: { 'Content-Type': 'application/json', 'X-Signup-Token': token },
            body: JSON.stringify(data),
        }
    )
    if (resp.ok) return null;
    else throw (await resp.text());
}


interface AccessToken {
    token: string;
}


export async function login(credentials: UserCredentials): Promise<AccessToken> {
    const resp = await fetch(
        `${BASE_API_URL}/login`,
        {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials),
        }
    )
    const respText = await resp.text();
    if (resp.ok) return JSON.parse(respText);
    else if (resp.status === 404) throw "Юзернейм не найден";
    else if (resp.status === 403) throw "Неправильный пароль";
    else throw respText;
}


export async function logout(): Promise<null> {
    const resp = await fetch(
        `${BASE_API_URL}/logout`,
        {
            headers: withAccessTokenHeader({}),
        }
    )
    if (resp.ok) return null;
    else throw (await resp.text());
}


interface SignupToken {
    creator_username: string | null;
    token: string;
}


export async function getMySignupToken(): Promise<SignupToken | null> {
    const resp = await fetch(
        `${BASE_API_URL}/signup-token`,
        {
            headers: withAccessTokenHeader({}),
        }
    )
    const respText = await resp.text();
    if (resp.ok) return JSON.parse(respText);
    else return null;
}


export async function generateSignupToken(): Promise<SignupToken> {
    const resp = await fetch(
        `${BASE_API_URL}/signup-token`,
        {
            method: "POST",
            headers: withAccessTokenHeader({}),
        }
    )
    const respText = await resp.text();
    if (resp.ok) return JSON.parse(respText);
    else throw (respText);
}


export interface CommentCoords {
    comment_id: string;
}


export async function starComment(coords: CommentCoords): Promise<null> {
    const resp = await fetch(
        `${BASE_API_URL}/starred-comments`,
        {
            method: "POST",
            headers: withAccessTokenHeader({}),
            body: JSON.stringify(coords),
        }
    )
    const respText = await resp.text();
    if (resp.ok) return null;
    else throw (respText);
}


export async function unstarComment(coords: CommentCoords): Promise<null> {
    const resp = await fetch(
        `${BASE_API_URL}/starred-comments`,
        {
            method: "DELETE",
            headers: withAccessTokenHeader({}),
            body: JSON.stringify(coords),
        }
    )
    const respText = await resp.text();
    if (resp.ok) return null;
    else throw (respText);
}

interface EditedComment {
    anchor_phrase: string | null,
    comment: string
}

interface EditCommentRequest {
    comment_id: string,
    edited_comment: EditedComment,
}


export async function editComment(request: EditCommentRequest): Promise<null> {
    const resp = await fetch(
        `${BASE_API_URL}/comment`,
        {
            method: "PUT",
            headers: withAccessTokenHeader({}),
            body: JSON.stringify(request),
        }
    )
    const respText = await resp.text();
    if (resp.ok) return null;
    else throw (respText);
}


interface EditTextRequest {
    id: string,
    text: string;
}


export async function editText(request: EditTextRequest): Promise<null> {
    const resp = await fetch(
        `${BASE_API_URL}/text`,
        {
            method: "PUT",
            headers: withAccessTokenHeader({}),
            body: JSON.stringify(request),
        }
    )
    const respText = await resp.text();
    if (resp.ok) return null;
    else throw (respText);
}


export enum SearchTextSorting {
    BEST_TO_WORST = "best_to_worst",
    START_TO_END = "start_to_end",
    END_TO_START = "end_to_start",
}

export enum SearchTextIn {
    TEXTS = "texts",
    COMMENTS = "comments",
}

export interface SearchTextRequest {
    query: string;
    page: number;
    page_size: number;
    sorting: SearchTextSorting;
    search_in: Array<SearchTextIn>;
    with_verse_parsha_data: boolean;
}

export interface FoundMatch {
    text: SingleText | null;
    comment: SingleComment | null;
    parsha_data: ParshaData | null;  // null = was not requested
}


export interface SearchTextResponse {
    found_matches: Array<FoundMatch>;
    total_matched_texts: number | null;
    total_matched_comments: number | null;
}

export async function searchText(request: SearchTextRequest): Promise<SearchTextResponse> {
    console.log(`Params for text search:`);
    console.log(request);
    let parts = new Array<string>();
    parts.push(`query=${encodeURIComponent(request.query)}`);
    parts.push(`page=${encodeURIComponent(request.page)}`);
    parts.push(`page_size=${encodeURIComponent(request.page_size)}`);
    parts.push(`sorting=${encodeURIComponent(request.sorting)}`);
    for (const searchInOption of request.search_in) {
        parts.push(`search_in=${encodeURIComponent(searchInOption)}`);

    }
    if (request.with_verse_parsha_data)
        parts.push(`with_verse_parsha_data=true`);
    const query = parts.join("&")
    const requestUrl = `${BASE_API_URL}/search-text?${query}`;
    console.log(`Generated request URL for text search: ${requestUrl}`)
    const resp = await fetch(requestUrl, { headers: withAccessTokenHeader({}) });
    const respText = await resp.text();
    if (resp.ok) return JSON.parse(respText);
    else throw (respText);
}


export interface StarredCommentData {
    comment: SingleComment;
    parsha_data: ParshaData;
}

export interface StarredCommentsMeta {
    total: number;
    random_starred_comment_data: StarredCommentData;
}

export async function getStarredCommentsMeta(): Promise<StarredCommentsMeta> {
    const resp = await fetch(`${BASE_API_URL}/starred-comments-meta`, { headers: withAccessTokenHeader({}) })
    const respText = await resp.text();
    if (resp.ok) return JSON.parse(respText);
    else throw (respText);
}
