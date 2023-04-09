import { CommentFilterByBookmarkMode, CommentSourcesConfig } from "./settings/commentSources";
import type { CommentData, Metadata, ParshaData, VerseData } from "./types";

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
            res.push({ chapter: chapterData.chapter, verse: verseData.verse })
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


export function signupPath(signupToken: string): string {
    return `/signup/${signupToken}`
}


export function versePath(parsha: number | string, verseCoords: VerseCoords): string {
    return `${parshaPath(parsha)}#${verseCoords2string(verseCoords)}`
}


export const sleep = (delaySec: number) => {
    return new Promise(resolve => setTimeout(resolve, delaySec * 1000))
}


export function commentPassesFilters(commentData: CommentData, commentSource: string, commentSourcesConfig: CommentSourcesConfig): boolean {
    if (commentSourcesConfig.filterByBookmarkMode == CommentFilterByBookmarkMode.MY && commentData.is_starred_by_me !== true) return false;
    if (commentSourcesConfig.filterBySource[commentSource] !== true) return false;
    return true;
}


export function anyCommentPassesFilters(verseData: VerseData, commentSourcesConfig: CommentSourcesConfig): boolean {
    for (const [commentSource, comments] of Object.entries(verseData.comments)) {
        for (const commentData of comments) {
            if (commentPassesFilters(commentData, commentSource, commentSourcesConfig)) return true;
        }
    }
    return false;
}


export function bookNoByParsha(parsha: number, metadata: Metadata): number {
    for (const [bookNo, parshaRange] of Object.entries(metadata.parsha_ranges)) {
        if (parsha >= parshaRange[0] && parsha < parshaRange[1]) {
            return parseInt(bookNo)
        }
    }
    throw Error(`No book found for parsha ${parsha}`)
}


export function isHebrewTextSource(textSource: string): boolean {
    return textSource == "hebrew"
}


export function toHebrewNumberal(i: number): string {
    // credits: https://hebrewnumerals.github.io/
    let result = "";
    var digits = (i.toString()).split("").reverse();

    // Hebrew Multiplier
    var multiplier = 0;

    // Hebrew Numerals
    var numerals = [
        //0   1    2    3    4    5    6    7    8    9
        ["", "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט"],       // x1
        ["", "י", "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ"],       // x10
        ["", "ק", "ר", "ש", "ת", "תק", "תר", "תש", "תת", "תתק"], // x100
        ["׳", "׳", "׳", "׳", "׳", "׳", "׳", "׳", "׳", "׳"]       // x1000
    ];

    // Loop through number array, reading each digit
    for (i = 0; i < digits.length; i++) {
        result = numerals[multiplier][digits[i]] + result;

        if (multiplier == 3) {
            // Reset the multiplier
            multiplier = 0;

            // Run the Convert again
            result = numerals[multiplier][digits[i]] + result;
        }

        multiplier++;
    }

    // 15 Filter
    result = result.replace("יה", "טו");
    // 16 Filter
    result = result.replace("יו", "טז");

    // Insert quote " before last character
    if (result.length > 1 &&  // Hebrew digit count must be greater than 1
        !result.endsWith("׳")  // Hebrew result must not end with Geresh ׳ for thousand 000
    ) {
        var len = result.length;
        result = result.substring(0, len - 1) + "\"" + result.substring(len - 1);
    }

    return result;
}


export function setPageTitle(subtitle: string | null) {
    const titleTags = document.getElementsByTagName("title");
    if (titleTags.length > 0) {
        if (subtitle !== null && subtitle.length > 0) {
            titleTags[0].innerText = `Тора | ${subtitle}`;
        } else {
            titleTags[0].innerText = `Тора`;
        }

    }
}
