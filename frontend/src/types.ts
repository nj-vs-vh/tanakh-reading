export enum CommentFormat {
    HTML = "html",
    MARKDOWN = "markdown",
    PLAIN = "plain",
}

interface CommentData {
    anchor_phrase: null | string;
    comment: string;
    format: CommentFormat;
}


export enum TextSource {
    FG = "fg"
}

export interface VerseData {
    verse: number;
    text: Map<TextSource, string>
    comments: Map<string, Array<CommentData>>
}


export interface ChapterData {
    chapter: number;
    verses: Array<VerseData>
}


export interface ParshaData {
    book: number;
    parsha: number;
    chapters: Array<ChapterData>
}


export interface Metadata {
    book_names: Map<number, Map<string, string>>;
    parsha_ranges: Map<number, Array<number>>;
    parsha_names: Map<number, Map<string, string>>;
    translation_about_links: Map<string, string>;
    translation_names: Map<string, string>;
    commenter_about_links: Map<string, string>;
    commenter_names: Map<string, string>;
    available_parsha: Array<number>;
}
