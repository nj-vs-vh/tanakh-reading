import type { TanakhSectionMetadata } from "./typesGenerated";

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

export enum SectionKey {
    TORAH = "torah",
    NEVIIM = "neviim"
}

export interface MultisectionMetadata {
    sections: Record<SectionKey, TanakhSectionMetadata>;
    available_parsha: Array<number>;
    logged_in_user: LoggedInUser | null;
}

export interface SectionMetadata {
    section: TanakhSectionMetadata;
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

export interface SingleText {
    db_id: string;
    text_coords: TextCoords;
    text_source: string;
    text: string;
    language: string;
}

export interface SingleComment {
    db_id: string;
    text_coords: TextCoords;
    comment_source: string;
    anchor_phrase: string | null;
    comment: string;
    format: CommentFormat;
    language: string;
    index: number;
    legacy_id: string | null;
    is_starred: boolean | null;
}

export interface CommentStarToggledEvent {
    commentId: string;
    newIsStarred: boolean;
}

export interface TextPositionFilter {
    parsha?: number;
    chapter?: number;
    verse?: number;
}

export interface TextOrCommentIterRequest {
    position: TextPositionFilter;
    source: string | null;
    offset: number;
}
