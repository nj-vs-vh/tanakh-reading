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


export interface VerseData {
    verse: number;
    text: Record<string, string>
    comments: Record<string, Array<CommentData>>
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
    book_names: Record<number, Record<string, string>>;
    parsha_ranges: Record<number, Array<number>>;
    parsha_names: Record<number, Record<string, string>>;
    text_sources: Array<string>;
    text_source_marks: Record<string, string>;
    text_source_descriptions: Record<string, string>;
    text_source_links: Record<string, Array<string>>;
    commenter_about_links: Record<string, string>;
    commenter_names: Record<string, string>;
    available_parsha: Array<number>;
}
