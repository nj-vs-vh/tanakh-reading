import { Writable, writable } from 'svelte/store';

export enum CommentStyle {
    ASTRERISK = "asterisk",
    CLICKABLE_TEXT = "clickableText",
}

const DEFAULT_COMMENT_STYLE = CommentStyle.ASTRERISK;

export const commentStyleStore: Writable<CommentStyle> = writable(DEFAULT_COMMENT_STYLE)


const LOCAL_STORAGE_KEY = 'commentStyle';


function loadCommentStyle(): CommentStyle {
    // @ts-ignore
    const saved: CommentStyle = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (saved === null)
        return DEFAULT_COMMENT_STYLE;
    else
        return saved;
}


function saveCommentStyle(style: CommentStyle) {
    localStorage.setItem(LOCAL_STORAGE_KEY, style);
}


export function initCommentStyle() {
    commentStyleStore.set(loadCommentStyle());
}


export function setCommentStyle(style: CommentStyle) {
    saveCommentStyle(style);
    commentStyleStore.set(style);
}
