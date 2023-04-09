export enum CommentFormat {
    HTML = "html",
    MARKDOWN = "markdown",
    PLAIN = "plain",
}

export interface CommentData {
    id: string;
    anchor_phrase: null | string;
    comment: string;
    format: CommentFormat;
    is_starred_by_me?: boolean;
}


export interface VerseData {
    verse: number;
    text: Record<string, string>;
    text_ids: Record<string, string>;
    comments: Record<string, Array<CommentData>>;
}


export interface ChapterData {
    chapter: number;
    verses: Array<VerseData>;
}


export interface ParshaData {
    book: number;
    parsha: number;
    chapters: Array<ChapterData>;
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
    is_editor: boolean;
}

// new style text and coords storage interfaces

export interface TextCoords {
    parsha: number;
    chapter: number;
    verse: number;
}

export interface FoundText {
    db_id: string;
    text_coords: TextCoords;
    text_source: string;
    text: string;
    language: string;
}

export interface FoundComment {
    db_id: string;
    text_coords: TextCoords;
    comment_source: string;
    anchor_phrase: string | null;
    comment: string;
    format: CommentFormat;
    language: string;
    index: number;
    legacy_id: string | null;
}

export interface CommentStarToggledEvent {
    commentId: string;
    newIsStarred: boolean;
}
