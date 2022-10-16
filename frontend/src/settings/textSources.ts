import { Writable, writable } from 'svelte/store';
import { Metadata, TextSource } from "../types";


interface TextSourcesConfig {
    main: TextSource;
    enabledInDetails: Partial<Record<TextSource, boolean>>;
}

export const textSourcesConfigStore: Writable<TextSourcesConfig> = writable({ main: TextSource.FG, enabledInDetails: { } })

const LOCAL_STORAGE_KEY = 'textSourcesConfig';


function saveConfig(config: TextSourcesConfig) {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(config));
}


export function initTextSourcesConfig(metadata: Metadata) {
    const configDump = localStorage.getItem(LOCAL_STORAGE_KEY);
    let config: TextSourcesConfig;
    if (configDump === null)
        config = {
            main: TextSource.FG,
            enabledInDetails: {},
        }
    else {
        config = JSON.parse(configDump);
        console.log(config);
    }

    for (const textSource of metadata.translations) {
        console.log(config.enabledInDetails);
        if (config.enabledInDetails[textSource] === undefined) {
            config.enabledInDetails[textSource] = true;
        }
    }
    textSourcesConfigStore.set(config);
    console.log(config);
    saveConfig(config);
}


export function setMainTextSource(newMainSource: TextSource) {
    textSourcesConfigStore.update(config => {
        config.main = newMainSource;
        saveConfig(config);
        return config;
    })
}


export function toggleTextSourceEnabled(source: TextSource) {
    textSourcesConfigStore.update(config => {
        config.enabledInDetails[source] = !config.enabledInDetails[source];
        saveConfig(config);
        return config;
    })
}


export function enableTextSource(source: TextSource) {
    textSourcesConfigStore.update(config => {
        config.enabledInDetails[source] = true;
        saveConfig(config);
        return config;
    })
}
