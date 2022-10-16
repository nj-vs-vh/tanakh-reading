import { Writable, writable } from 'svelte/store';

export enum CommentStyle {
    MODAL = "modal",
    INLINE = "inline",
}

const DEFAULT_STYLE = CommentStyle.MODAL;

export const commentStyleStore: Writable<CommentStyle> = writable(DEFAULT_STYLE)

const LOCAL_STORAGE_KEY = 'commentStyle';


export function initCommentStyle() {
    // @ts-ignore
    let style: CommentStyle | null = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (style === null)
        style = DEFAULT_STYLE;
    commentStyleStore.set(style);
}


export function setCommentStyle(style: CommentStyle) {
    localStorage.setItem(LOCAL_STORAGE_KEY, style);
    commentStyleStore.set(style);
}
