import { Writable, writable } from 'svelte/store';
import type { MultisectionMetadata, SectionKey, SectionMetadata } from "../types";


interface SectionTextSourcesConfig {
    main: string;
    enabledInDetails: Record<string, boolean>;
}

type TextSourcesConfig = Record<SectionKey, SectionTextSourcesConfig>;

const DEFAULT_TEXT_SOURCES_CONFIG: TextSourcesConfig = {
    "torah": { main: "fg", enabledInDetails: {} },
    "neviim": { main: "mosad-harav-cook", enabledInDetails: {} },
}

export const textSourcesConfigStore: Writable<TextSourcesConfig> = writable(DEFAULT_TEXT_SOURCES_CONFIG)

const LOCAL_STORAGE_KEY = 'textSourcesConfig';


function saveConfig(config: TextSourcesConfig) {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(config));
}


export function initTextSourcesConfig(metadata: MultisectionMetadata) {
    const configDump = localStorage.getItem(LOCAL_STORAGE_KEY);
    let config: TextSourcesConfig;
    if (configDump === null)
        config = DEFAULT_TEXT_SOURCES_CONFIG
    else {
        config = JSON.parse(configDump);
    }

    // migration from single-section config to multi-section
    if (config.enabledInDetails !== undefined) {
        config = {
            // @ts-expect-error
            torah: { ...config },
            neviim: DEFAULT_TEXT_SOURCES_CONFIG.neviim,
        }
    }

    for (const [key, sectionConfig] of Object.entries(config)) {
        const sectionKey = key as SectionKey;
        for (const textSourceInfo of metadata.sections[sectionKey].text_sources) {
            if (sectionConfig.enabledInDetails[textSourceInfo.key] === undefined) {
                sectionConfig.enabledInDetails[textSourceInfo.key] = true;
            }
        }
    }
    textSourcesConfigStore.set(config);
    saveConfig(config);
}


export function setMainTextSource(sectionKey: SectionKey, newMainSource: string) {
    textSourcesConfigStore.update(config => {
        config[sectionKey].main = newMainSource;
        saveConfig(config);
        return config;
    })
}


export function toggleTextSourceEnabled(sectionKey: SectionKey, source: string) {
    textSourcesConfigStore.update(config => {
        config[sectionKey].enabledInDetails[source] = !config[sectionKey].enabledInDetails[source];
        saveConfig(config);
        return config;
    })
}


export function enableTextSource(sectionKey: SectionKey, source: string) {
    textSourcesConfigStore.update(config => {
        config[sectionKey].enabledInDetails[source] = true;
        saveConfig(config);
        return config;
    })
}
