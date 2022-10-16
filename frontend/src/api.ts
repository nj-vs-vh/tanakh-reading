import { isProduction } from "./config";
import type { ParshaData, Metadata } from "./types";


// @ts-ignore
const BASE_API_URL = isProduction ? "https://torah-reading-backend.herokuapp.com" : "http://localhost:8081";
const NETWORKING_ERRMSG = "Ошибка подключения, попробуйте обновить страницу!";


export async function getParsha(index: number): Promise<ParshaData | string> {
    console.log(`Fetching parsha index ${index}`)
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
        console.warn(`Error fetching parsha data: ${error}`)
        return NETWORKING_ERRMSG;
    }
}


export async function getMetadata(): Promise<Metadata | string> {
    console.log(`Fetching metadata`)
    try {
        const resp = await fetch(
            `${BASE_API_URL}/metadata`,
            { headers: { 'Content-Type': 'application/json' } }
        )
        const respText = await resp.text();

        if (resp.ok) {
            return JSON.parse(respText);
        } else {
            return respText;
        }
    } catch (error) {
        console.warn(`Error fetching metadata: ${error}`)
        return NETWORKING_ERRMSG;
    }
}
