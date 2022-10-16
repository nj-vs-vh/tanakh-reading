import { Writable, writable } from 'svelte/store';
import type { Metadata } from './types';

export type CommentSourceFlags = Map<string, boolean>

export const commentSourceFlagsStore: Writable<CommentSourceFlags> = writable(new Map())

const LOCAL_STORAGE_KEY = 'activeCommentSources';


function loadCommentSourceFlags(): CommentSourceFlags {
    const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (saved === null)
        return new Map();
    else
        return JSON.parse(saved);
}


function saveCommentSourceFlags(current: CommentSourceFlags) {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(current));
}


export function initCommentSourceFlags(metadata: Metadata) {
    const flags = loadCommentSourceFlags();
    for (const commenter of Object.keys(metadata.commenter_names)) {
        if (flags[commenter] === undefined) {
            flags[commenter] = true;  // initializing new, previously unknown commenters with True
        }
    }

    commentSourceFlagsStore.set(flags);
    saveCommentSourceFlags(flags);
}


export function toggleCommentSourceFlag(commentSource: string) {
    commentSourceFlagsStore.update(current => {
        if (current[commentSource] == undefined) {
            return current;
        } else {
            current[commentSource] = !current[commentSource];
            saveCommentSourceFlags(current);
            return current;
        }
    });
}
