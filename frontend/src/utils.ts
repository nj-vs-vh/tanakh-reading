import type { ParshaData } from "./types";

export function getUrlHash(): string {
    const url = new URL(window.location.href);
    return url.hash.slice(1, url.hash.length);
}


export function setUrlHash(hash: string) {
    const url = new URL(window.location.href);
    const urlHash = hash.startsWith("#") ? hash : `#${hash}`;
    url.hash = urlHash;
    window.location.href = url.href;
}


export interface VerseCoords {
    chapter: number;
    verse: number;
}

export function verseCoords2string(vc: VerseCoords): string {
    return `${vc.chapter}:${vc.verse}`
}

export function string2verseCoords(s: string): VerseCoords | null {
    const regex = /^(\d+):(\d+)$/;
    const matchArr = s.match(regex);
    if (matchArr === null) return null;
    else {
        try {
            return {
                chapter: parseInt(matchArr[1]),
                verse: parseInt(matchArr[2]),
            }
        } catch {
            return null
        }
    }
}


export function getUrlHashVerseCoords(): VerseCoords | null {
    return string2verseCoords(getUrlHash());
}

export function getVerseCoords(parshaData: ParshaData): VerseCoords[] {
    const res: VerseCoords[] = [];
    for (const chapterData of parshaData.chapters) {
        for (const verseData of chapterData.verses) {
            res.push({chapter: chapterData.chapter, verse: verseData.verse})
        }
    }
    res.sort(cmpVerseCoords)
    return res;
}

export function areInsideVerseCoordsList(vc: VerseCoords, vcList: VerseCoords[]): boolean {
    for (const vcTry of vcList) {
        if (vc.chapter === vcTry.chapter && vc.verse === vcTry.verse) {
            return true;
        }
    }
    return false;
}

export function cmpVerseCoords(a: VerseCoords, b: VerseCoords): number {
    if (a.chapter > b.chapter) return 1;
    else if (a.chapter < b.chapter) return -1;
    else {
        if (a.verse > b.verse) return 1;
        else if (a.verse < b.verse) return -1;
        else return 0;
    }
}


export const range = (start: number, end: number): number[] => {
    const length = end - start;
    return Array.from({ length }, (_, i) => start + i);
};


export function parshaPath(parsha: number | string): string {
    return `/parsha/${parsha}`
}


export function versePath(parsha: number | string, verseCoords: VerseCoords): string {
    return `${parshaPath(parsha)}#${verseCoords2string(verseCoords)}`
}
