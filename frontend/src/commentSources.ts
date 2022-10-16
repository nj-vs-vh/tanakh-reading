import { Writable, writable } from 'svelte/store';
import type { Metadata } from './types';


export const commentSourceFlagsStore: Writable<CommentSourceFlags> = writable(new Map())


const STORED_ACTIVE_COMMENT_SOURCES = 'activeCommentSources';
export type CommentSourceFlags = Map<string, boolean>


function loadCommentSourceFlags(): CommentSourceFlags {
    const saved = localStorage.getItem(STORED_ACTIVE_COMMENT_SOURCES);
    if (saved === null)
        return new Map();
    else
        return JSON.parse(saved);
}


function saveCommentSourceFlags(current: CommentSourceFlags) {
    localStorage.setItem(STORED_ACTIVE_COMMENT_SOURCES, JSON.stringify(current));
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
