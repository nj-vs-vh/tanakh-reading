import { withAccessTokenHeader } from "./auth";
import { isProduction } from "./config";
import type { ParshaData, Metadata, SignupData, UserCredentials } from "./types";


// @ts-ignore
const BASE_API_URL = isProduction ? "https://torah-reading-backend.herokuapp.com" : "http://localhost:8081";
const NETWORKING_ERRMSG = "Ошибка подключения, попробуйте обновить страницу!";


export async function getParsha(index: number): Promise<ParshaData | string> {
    console.log(`Fetching parsha index ${index}`);
    try {
        const resp = await fetch(
            `${BASE_API_URL}/parsha/${index}`,
            { headers: { 'Content-Type': 'application/json' } }
        )
        const respText = await resp.text();

        if (resp.ok) {
            return JSON.parse(respText);
        } else {
            return respText;
        }
    } catch (error) {
        console.warn(`Error making request: ${error}`);
        return NETWORKING_ERRMSG;
    }
}


export async function getMetadata(): Promise<Metadata | string> {
    console.log(`Fetching metadata`);
    try {
        const resp = await fetch(
            `${BASE_API_URL}/metadata`,
            { headers: withAccessTokenHeader({ 'Content-Type': 'application/json' }) }
        )
        const respText = await resp.text();

        if (resp.ok) {
            return JSON.parse(respText);
        } else {
            return respText;
        }
    } catch (error) {
        console.warn(`Error making request: ${error}`);
        return NETWORKING_ERRMSG;
    }
}


export async function checkSignupToken(token: string): Promise<boolean | string> {
    console.log(`Checking signup token`);
    const resp = await fetch(
        `${BASE_API_URL}/check-signup-token`,
        { headers: { 'Content-Type': 'application/json', 'X-Signup-Token': token } }
    )
    return resp.ok;
}


export async function signup(token: string, data: SignupData): Promise<string | null> {
    console.log(`Signing up`);
    try {
        const resp = await fetch(
            `${BASE_API_URL}/signup`,
            {
                method: "POST",
                headers: { 'Content-Type': 'application/json', 'X-Signup-Token': token },
                body: JSON.stringify(data),
            }
        )
        if (resp.ok) return null;
        else return await resp.text()
    } catch (error) {
        console.warn(`Error making request: ${error}`);
        return NETWORKING_ERRMSG;
    }
}


export interface AccessToken {
    token: string;
}


export async function login(credentials: UserCredentials): Promise<string | AccessToken> {
    console.log(`Logging in`);
    try {
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
        else if (resp.status === 404) return "Юзернейм не найден";
        else if (resp.status === 403) return "Неправильный пароль";
        else return respText;
    } catch (error) {
        console.warn(`Error making request: ${error}`);
        return NETWORKING_ERRMSG;
    }
}


export async function logout(): Promise<string | null> {
    console.log(`Logging out`);
    try {
        const resp = await fetch(
            `${BASE_API_URL}/logout`,
            {
                headers: withAccessTokenHeader({}),
            }
        )
        if (resp.ok) return null;
        else return await resp.text();
    } catch (error) {
        console.warn(`Error making request: ${error}`);
        return NETWORKING_ERRMSG;
    }
}
