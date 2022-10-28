import { withAccessTokenHeader } from "./auth";
import { isProduction } from "./config";
import type { ParshaData, Metadata, SignupData, UserCredentials } from "./types";


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


export interface FullCommentCoords {
    comment_id: string;
    parsha: number;
    chapter: number;
    verse: number;
}


export async function starComment(coords: FullCommentCoords): Promise<null> {
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


export async function unstarComment(coords: FullCommentCoords): Promise<null> {
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
