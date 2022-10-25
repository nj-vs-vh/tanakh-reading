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
    // book idx -> [parshas included]
    parsha_ranges: Record<number, Array<number>>;
    // parsha idx -> [[start chapter, verse], [end chapter, verse]]
    chapter_verse_ranges: Record<number, Array<Array<number>>>;
    parsha_names: Record<number, Record<string, string>>;
    text_sources: Array<string>;
    text_source_marks: Record<string, string>;
    text_source_descriptions: Record<string, string>;
    text_source_links: Record<string, Array<string>>;
    commenter_links: Record<string, Array<string>>;
    commenter_names: Record<string, string>;
    available_parsha: Array<number>;
    logged_in_user: LoggedInUser | null;
}


export interface UserCredentials {
    username: string;
    password: string;
}


export interface UserData {
    full_name: string;
}


export interface SignupData {
    credentials: UserCredentials;
    data: UserData;
}


export interface LoggedInUser {
    username: string;
    data: UserData;
    invited_by_username: string;
}
