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

interface VerseData {
    verse: number;
    text: Map<TextSource, string>
    comments: Map<string, Array<CommentData>>
}


interface ChapterData {
    chapter: number;
    verses: Array<VerseData>
}


export interface ParshaData {
    book: number;
    parsha: number;
    chapters: Array<ChapterData>
}
