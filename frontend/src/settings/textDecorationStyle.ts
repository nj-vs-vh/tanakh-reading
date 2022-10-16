import { Writable, writable } from 'svelte/store';

export enum TextDecorationStyle {
    ASTRERISK = "asterisk",
    CLICKABLE_TEXT = "clickableText",
}

const DEFAULT_STYLE = TextDecorationStyle.ASTRERISK;

export const textDecorationStyleStore: Writable<TextDecorationStyle> = writable(DEFAULT_STYLE)


const LOCAL_STORAGE_KEY = 'textDecorationStyle';


function loadStyle(): TextDecorationStyle {
    // @ts-ignore
    const saved: TextDecorationStyle = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (saved === null)
        return DEFAULT_STYLE;
    else
        return saved;
}


function saveStyle(style: TextDecorationStyle) {
    localStorage.setItem(LOCAL_STORAGE_KEY, style);
}


export function initTextDecorationStyle() {
    textDecorationStyleStore.set(loadStyle());
}


export function setTextDecorationStyle(style: TextDecorationStyle) {
    saveStyle(style);
    textDecorationStyleStore.set(style);
}
