import { withAccessTokenHeader } from "./auth";
import { isProduction } from "./config";
import type { ParshaData, Metadata, SignupData, UserCredentials } from "./types";


// @ts-ignore
const BASE_API_URL = isProduction ? "https://torah-reading-backend.herokuapp.com" : "http://localhost:8081";


export async function getParsha(index: number): Promise<ParshaData> {
    console.log(`Fetching parsha index ${index}`);
    const resp = await fetch(
        `${BASE_API_URL}/parsha/${index}`,
        { headers: { 'Content-Type': 'application/json' } }
    )
    const respText = await resp.text();
    if (resp.ok)
        return JSON.parse(respText);
    else
        throw (respText);
}


export async function getMetadata(): Promise<Metadata> {
    console.log(`Fetching metadata`);
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
    console.log(`Checking signup token`);
    const resp = await fetch(
        `${BASE_API_URL}/check-signup-token`,
        { headers: { 'Content-Type': 'application/json', 'X-Signup-Token': token } }
    )
    return resp.ok;
}


export async function signup(token: string, data: SignupData): Promise<null> {
    console.log(`Signing up`);
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


export async function login(credentials: UserCredentials): Promise<string> {
    console.log(`Logging in`);
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
    console.log(`Logging out`);
    const resp = await fetch(
        `${BASE_API_URL}/logout`,
        {
            headers: withAccessTokenHeader({}),
        }
    )
    if (resp.ok) return null;
    else throw (await resp.text());
}


// export async function getMySignupToken(): Promise<string> {

// }
