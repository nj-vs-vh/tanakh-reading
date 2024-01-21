import { Writable, writable } from 'svelte/store';

export interface TextDecorationSettings {
    onlyDecorateTextWithComments: boolean; // including user comments
}

const DEFAULT_TEXT_DECORATION_SETTINGS: TextDecorationSettings = {
    onlyDecorateTextWithComments: false,
}

export const textDecorationSettingsStore: Writable<TextDecorationSettings> = writable(DEFAULT_TEXT_DECORATION_SETTINGS)

const LOCAL_STORAGE_KEY = 'textDecorationSettings';


function load(): TextDecorationSettings {
    const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (saved === null)
        return DEFAULT_TEXT_DECORATION_SETTINGS;
    else
        return JSON.parse(saved);
}


function save(current: TextDecorationSettings) {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(current));
}


export function initTextDecorationSettings() {
    const loaded = load();
    textDecorationSettingsStore.set(loaded);
}


export function setTextDecorationSettings(newSettings: TextDecorationSettings) {
    textDecorationSettingsStore.set(newSettings);
    save(newSettings);
}
