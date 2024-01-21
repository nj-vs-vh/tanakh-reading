/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type IsoLang = "ru" | "en" | "he";

export interface CommentSource {
  key: string;
  name: string;
  links: string[];
  language: IsoLang;
}
export interface ParshaInfo {
  id: number;
  book_id: number;
  /**
   * @minItems 2
   * @maxItems 2
   */
  chapter_verse_start: [number, number];
  /**
   * @minItems 2
   * @maxItems 2
   */
  chapter_verse_end: [number, number];
  name: {
    [k: string]: string;
  };
  url_name: string;
  parsha_group_leader_id?: number;
}
export interface TanakhBookInfo {
  id: number;
  name: {
    [k: string]: string;
  };
}
export interface TanakhSectionMetadata {
  title: {
    [k: string]: string;
  };
  subtitle?: {
    [k: string]: string;
  };
  text_sources: TextSource[];
  comment_sources: CommentSource[];
  books: TanakhBookInfo[];
  parshas: ParshaInfo[];
}
export interface TextSource {
  key: string;
  mark: string;
  description: string;
  links: string[];
  language: IsoLang;
}
