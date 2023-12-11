import { Writable, writable } from 'svelte/store';
import type { MultisectionMetadata, SectionKey } from '../types';


export enum CommentFilterByBookmarkMode {
    NONE = "Выкл.",
    MY = "Только мои закладки",
    // GROUP = "group",
}

export interface SectionCommentSourcesConfig {
    filterBySource: Record<string, boolean>;
    filterByBookmarkMode: CommentFilterByBookmarkMode;
    sourcesOrder: Array<string>,
}

type CommentSourcesConfig = Record<SectionKey, SectionCommentSourcesConfig>;


const DEFAULT_COMMENT_SOURCES_CONFIG: CommentSourcesConfig = {
    "torah": {
        filterBySource: {},
        filterByBookmarkMode: CommentFilterByBookmarkMode.NONE,
        sourcesOrder: [],
    },
    "neviim": {
        filterBySource: {},
        filterByBookmarkMode: CommentFilterByBookmarkMode.NONE,
        sourcesOrder: [],
    }
};


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


export function initCommentSourcesConfig(metadata: MultisectionMetadata) {
    let config = load();

    // migration from single-section metadata
    if (config.filterByBookmarkMode !== undefined) {
        config = {
            // @ts-expect-error
            torah: { ...config },
            neviim: DEFAULT_COMMENT_SOURCES_CONFIG.neviim
        };
    }

    // ensuring the config is complete and resetting things to default if necessary
    for (const [key, sectionConfig] of Object.entries(config)) {
        const sectionKey = key as SectionKey;
        const allSectionCommentSourceKeys = metadata.sections[sectionKey].comment_sources.map(cs => cs.key);
        for (const commentSource of allSectionCommentSourceKeys) {
            if (sectionConfig.filterBySource[commentSource] === undefined) {
                sectionConfig.filterBySource[commentSource] = true;
            }
        }
        if (sectionConfig.sourcesOrder === undefined || sectionConfig.sourcesOrder.length != allSectionCommentSourceKeys.length) {
            sectionConfig.sourcesOrder = allSectionCommentSourceKeys;
        }
    }

    commentSourcesConfigStore.set(config);
    save(config);
}


export function toggleCommentFilterBySource(sectionKey: SectionKey, commentSource: string) {
    commentSourcesConfigStore.update(config => {
        if (config[sectionKey].filterBySource[commentSource] === undefined) {
            return config;
        } else {
            config[sectionKey].filterBySource[commentSource] = !config[sectionKey].filterBySource[commentSource];
            save(config);
            return config;
        }
    });
}


export function setCommentFilterBySource(sectionKey: SectionKey, bySource: Record<string, boolean>) {
    commentSourcesConfigStore.update(config => {
        config[sectionKey].filterBySource = bySource;
        save(config);
        return config;
    });
}


export function setCommentFilterByBookmarkMode(sectionKey: SectionKey, mode: CommentFilterByBookmarkMode) {
    commentSourcesConfigStore.update(config => {
        config[sectionKey].filterByBookmarkMode = mode;
        save(config);
        return config;
    });
}

export function swapElementsInSourceOrder(sectionKey: SectionKey, oldIndex: number, newIndex: number) {
    commentSourcesConfigStore.update(config => {
        let sourcesOrder = [...config[sectionKey].sourcesOrder];
        const el = sourcesOrder[oldIndex];
        console.log(`Moving ${el} ${oldIndex} -> ${newIndex}; before: ${sourcesOrder}`)
        sourcesOrder.splice(oldIndex, 1);
        sourcesOrder.splice(newIndex, 0, el)
        console.log(`...after: ${sourcesOrder}`)
        config[sectionKey].sourcesOrder = [...sourcesOrder];
        save(config);
        return config;
    })
}
