import { Writable, writable } from 'svelte/store';

export enum TextDecorationStyle {
    ASTRERISK = "asterisk",
    CLICKABLE_TEXT = "clickableText",
    NONE = "none",
}

const DEFAULT_STYLE = TextDecorationStyle.ASTRERISK;

export const textDecorationStyleStore: Writable<TextDecorationStyle> = writable(DEFAULT_STYLE)

const LOCAL_STORAGE_KEY = 'textDecorationStyle';


export function initTextDecorationStyle() {
    // @ts-ignore
    let style: TextDecorationStyle = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (style === null)
        style = DEFAULT_STYLE;
    textDecorationStyleStore.set(style);
}


export function setTextDecorationStyle(style: TextDecorationStyle) {
    localStorage.setItem(LOCAL_STORAGE_KEY, style);
    textDecorationStyleStore.set(style);
}
