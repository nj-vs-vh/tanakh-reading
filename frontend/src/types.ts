import type { TanakhSectionMetadata } from "./typesGenerated";

export enum Format {
    HTML = "html",
    PLAIN = "plain",
}

export interface CommentData {
    id: string;
    anchor_phrase: null | string;
    comment: string;
    format: Format;
    is_starred_by_me?: boolean;
}

export interface VerseData {
    verse: number;
    text: Record<string, string>;
    text_ids: Record<string, string>;
    text_formats: Record<string, Format>;
    comments: Record<string, Array<CommentData>>;

    user_comments?: Array<DisplayedUserComment>;
}

export interface UserCommentPayload {
    text_coords: TextCoords;
    anchor_phrase: string | null;
    comment: string;
}

export interface StoredUserComment extends UserCommentPayload {
    db_id: string;
    author_username: string;
    timestamp: string;  // iso-format datetime string
}


export interface DisplayedUserComment extends StoredUserComment {
    author_user_data: UserData
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

enum KnownSectionKey {
    TORAH = "torah",
    NEVIIM = "neviim"
}

// NOTE: arbitrary section key is allowed but we want to handle known cases in the code and get autocompletion from enum
export type SectionKey = KnownSectionKey | string;

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

export function toSingleSection(metadata: MultisectionMetadata, sectionKey: SectionKey): SectionMetadata {
    return {
        section: metadata.sections[sectionKey],
        available_parsha: metadata.available_parsha,
        logged_in_user: metadata.logged_in_user,
    }
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
    format: Format;
}

export interface SingleComment {
    db_id: string;
    text_coords: TextCoords;
    comment_source: string;
    anchor_phrase: string | null;
    comment: string;
    format: Format;
    language: string;
    index: number;
    legacy_id: string | null;
    is_starred: boolean | null;
}

export interface CommentStarToggledEvent {
    commentId: string;
    newIsStarred: boolean;
}

export interface UserCommentEvent {
    chapter: number;
    verse: number;
    userCommentId: string;
    action: "created" | "deleted";
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
