import { Writable, writable } from 'svelte/store';
import type { Metadata } from '../types';


export enum CommentFilterByBookmarkMode {
    NONE = "Выкл.",
    MY = "Только мои закладки",
    // GROUP = "group",
}

export interface CommentFilters {
    bySource: Record<string, boolean>;
    byBookmarkMode: CommentFilterByBookmarkMode;
}


const DEFAULT_COMMENT_FILERS: CommentFilters = {
    bySource: {},
    byBookmarkMode: CommentFilterByBookmarkMode.NONE,
}


export const commentFiltersStore: Writable<CommentFilters> = writable(DEFAULT_COMMENT_FILERS);

const LOCAL_STORAGE_KEY = 'commentFilters';


function load(): CommentFilters {
    const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (saved === null)
        return DEFAULT_COMMENT_FILERS;
    else
        return JSON.parse(saved);
}


function save(current: CommentFilters) {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(current));
}


export function initCommentFilters(metadata: Metadata) {
    const filters = load();
    for (const commenter of Object.keys(metadata.commenter_names)) {
        if (filters.bySource[commenter] === undefined) {
            filters.bySource[commenter] = true;
        }
    }

    commentFiltersStore.set(filters);
    save(filters);
}


export function toggleCommentFilterBySource(commentSource: string) {
    commentFiltersStore.update(current => {
        if (current.bySource[commentSource] === undefined) {
            return current;
        } else {
            current.bySource[commentSource] = !current.bySource[commentSource];
            save(current);
            return current;
        }
    });
}


export function setCommentFilterBySource(bySource: Record<string, boolean>) {
    commentFiltersStore.update(current => {
        current.bySource = bySource;
        save(current);
        return current;
    });
}


export function setCommentFilterByBookmarkMode(mode: CommentFilterByBookmarkMode) {
    commentFiltersStore.update(current => {
        current.byBookmarkMode = mode;
        save(current);
        return current;
    });
}
