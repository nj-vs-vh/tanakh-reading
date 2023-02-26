import { Writable, writable } from 'svelte/store';
import type { Metadata } from '../types';


export enum CommentFilterByBookmarkMode {
    NONE = "Выкл.",
    MY = "Только мои закладки",
    // GROUP = "group",
}

export interface CommentSourcesConfig {
    filterBySource: Record<string, boolean>;
    filterByBookmarkMode: CommentFilterByBookmarkMode;
    sourcesOrder: Array<string>,
}


const DEFAULT_COMMENT_SOURCES_CONFIG: CommentSourcesConfig = {
    filterBySource: {},
    filterByBookmarkMode: CommentFilterByBookmarkMode.NONE,
    sourcesOrder: [],
}


export const commentSourcesConfigStore: Writable<CommentSourcesConfig> = writable(DEFAULT_COMMENT_SOURCES_CONFIG);

const LOCAL_STORAGE_KEY = 'commentFilters';


function load(): CommentSourcesConfig {
    const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (saved === null)
        return DEFAULT_COMMENT_SOURCES_CONFIG;
    else {
        return JSON.parse(saved);
    }
}


function save(current: CommentSourcesConfig) {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(current));
}


export function initCommentSourcesConfig(metadata: Metadata) {
    const config = load();

    // migration from old fields
    if (config.filterByBookmarkMode === undefined) {
        // @ts-ignore
        config.filterByBookmarkMode = config.byBookmarkMode;
        // @ts-ignore
        config.filterBySource = config.bySource;
    }

    const metadataCommentSources = Object.keys(metadata.commenter_names);
    for (const commentSource of metadataCommentSources) {
        if (config.filterBySource[commentSource] === undefined) {
            config.filterBySource[commentSource] = true;
        }
    }
    if (config.sourcesOrder === undefined || config.sourcesOrder.length != metadataCommentSources.length) {
        config.sourcesOrder = metadataCommentSources;
    }

    commentSourcesConfigStore.set(config);
    save(config);
}


export function toggleCommentFilterBySource(commentSource: string) {
    commentSourcesConfigStore.update(current => {
        if (current.filterBySource[commentSource] === undefined) {
            return current;
        } else {
            current.filterBySource[commentSource] = !current.filterBySource[commentSource];
            save(current);
            return current;
        }
    });
}


export function setCommentFilterBySource(bySource: Record<string, boolean>) {
    commentSourcesConfigStore.update(current => {
        current.filterBySource = bySource;
        save(current);
        return current;
    });
}


export function setCommentFilterByBookmarkMode(mode: CommentFilterByBookmarkMode) {
    commentSourcesConfigStore.update(current => {
        current.filterByBookmarkMode = mode;
        save(current);
        return current;
    });
}

export function swapElementsInSourceOrder(oldIndex: number, newIndex: number) {
    commentSourcesConfigStore.update(current => {
        let sourcesOrder = [...current.sourcesOrder];
        const el = sourcesOrder[oldIndex];
        console.log(`Moving ${el} ${oldIndex} -> ${newIndex}; before: ${sourcesOrder}`)
        sourcesOrder.splice(oldIndex, 1);
        sourcesOrder.splice(newIndex, 0, el)
        console.log(`...after: ${sourcesOrder}`)
        current.sourcesOrder = [...sourcesOrder];
        save(current);
        return current;
    })
}
