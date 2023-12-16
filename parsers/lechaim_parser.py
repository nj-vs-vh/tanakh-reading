"""Parser for https://lechaim.ru/torah/ """

import argparse
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional, cast

import requests  # type: ignore
from bs4 import BeautifulSoup, Tag  # type: ignore

from backend.metadata import TorahCommentSource, TorahTextSource, get_book_by_parsha
from backend.model import ChapterData, CommentData, ParshaData, VerseData
from parsers.merge import merge_and_save_parsha_data
from parsers.utils import (
    dump_parsha,
    has_class,
    has_class_that,
    inner_tag_text,
    postprocess_patched_text,
    tag_filter,
)

HTML_DIR = Path("html/lechaim")
HTML_DIR.mkdir(exist_ok=True)


def get_per_day_htmls(parsha: int, parsha_url_path: str, allow_incomplete: bool) -> list[BeautifulSoup]:
    parsha_htmls_dir = HTML_DIR / str(parsha)
    parsha_htmls_dir.mkdir(exist_ok=True)

    res: list[BeautifulSoup] = []
    for day in range(1, 8):
        html = parsha_htmls_dir / f"day{day}.html"
        if not html.exists():
            if allow_incomplete:
                continue
            url = f"https://lechaim.ru/academy/{parsha_url_path}{day}/"
            print(f"Downloading parsha HTML for day {day} from {url}...")
            resp = requests.get(url)
            if resp.status_code != 200:
                raise ValueError(f"Non-200 status for {resp}")
            html.write_bytes(resp.content)
        res.append(BeautifulSoup(html.read_text(), features="html.parser"))
    if not res:
        raise ValueError("allow incomplete = True but not a single file found")
    return res


def parse(parsha: int, parsha_url_path: str, allow_incomplete: bool):
    parsha_data = ParshaData(book=get_book_by_parsha(parsha), parsha=parsha, chapters=[])

    chapter_data_by_chapter: dict[int, ChapterData] = dict()

    parsha_day_docs = get_per_day_htmls(parsha, parsha_url_path, allow_incomplete=allow_incomplete)
    for parsha_day_doc in parsha_day_docs:
        for chapter_container in parsha_day_doc.find_all(tag_filter("div", ["article-part_text"])):
            chapter_container = cast(Tag, chapter_container)
            chapter_header = chapter_container.find(tag_filter("h3", ["article-part_title"]))

            chapter = int(inner_tag_text(chapter_header).removeprefix("Глава").strip())
            if chapter in chapter_data_by_chapter:
                chapter_data = chapter_data_by_chapter[chapter]
                add_chapter_to_parsha = False
            else:
                chapter_data = ChapterData(
                    chapter=chapter,
                    verses=[],
                )
                chapter_data_by_chapter[chapter] = chapter_data
                add_chapter_to_parsha = True
            for verse_container in chapter_container.find_all(tag_filter("li", ["article-part_item"])):
                verse_container = cast(Tag, verse_container)
                verse_number_el = verse_container.find(tag_filter("input", []))
                verse_text_container = verse_container.find(tag_filter("div", ["article-part_translated"]))
                verse_data = VerseData(
                    verse=int(verse_number_el.attrs["value"]),
                    text={
                        TorahTextSource.LECHAIM: inner_tag_text(verse_text_container),
                    },
                    comments=defaultdict(list),
                )

                def parse_comment_paragraph(maybe_comment_paragraph: Tag) -> tuple[str, Optional[str], str]:
                    #                                                            class, anchor phrase, comment html
                    if not isinstance(maybe_comment_paragraph, Tag) or not has_class_that(
                        maybe_comment_paragraph, lambda css_class: "-comment" in css_class
                    ):
                        raise ValueError("not a comment")
                    css_class = maybe_comment_paragraph.attrs["class"][0]
                    # hopefully, rashi, editor or ezra
                    css_class_prefix = re.sub(r"-comment.*", "", css_class)
                    anchor_phrase: Optional[str] = None
                    comment_html = ""
                    for child in maybe_comment_paragraph.children:
                        if has_class_that(child, lambda c: c.endswith("-translation-fragment")):
                            anchor_phrase = inner_tag_text(child)
                        elif has_class(child, "article-part_text-marked"):
                            comment_html += f"[<i>{inner_tag_text(child)}</i>]"
                        else:
                            comment_html += str(child)
                    return css_class_prefix, anchor_phrase, postprocess_patched_text(comment_html)

                for comments_container in verse_container.find_all(
                    tag_filter("div", required_classes=["article-part_tab-content"])
                ):
                    comments_container = cast(Tag, comments_container)

                    if any(ch.name == "p" for ch in comments_container.children if isinstance(ch, Tag)):
                        # normal structure of the container:
                        # <div class="article-part_comment-main"> [verse text copy] </div>
                        # <p class="rashi-comment"> ... </p>
                        # <p class="ezra-comment"> ... </p>
                        maybe_comments_iter = comments_container.children
                    else:
                        # alternative structure
                        # <div class="article-part_comment-main"> [verse text copy] </div>
                        # ... plain rashi comment
                        # in this case we remove the div and use the whole comments_container
                        # as a single rashi comment
                        print(
                            "Detected alternative comment structure for "
                            + f"{chapter_data['chapter']}:{verse_data['verse']}"
                        )
                        for div in comments_container.find_all(  # yes, this naming is confusing
                            tag_filter("div", required_classes=["article-part_comment-main"])
                        ):
                            if isinstance(div, Tag):
                                div.decompose()
                        # faking the way paragraphs are class-ed in the normal layout
                        comments_container.attrs["class"].insert(0, "rashi-comment")
                        maybe_comments_iter = [comments_container]

                    current_comment_data: Optional[CommentData] = None
                    current_comment_source: Optional[str] = None
                    for child in maybe_comments_iter:
                        try:
                            css_class_prefix, anchor_phrase, comment_html = parse_comment_paragraph(child)
                        except Exception:
                            continue

                        if css_class_prefix == "rashi" or css_class_prefix == "editor":
                            new_comment_source = TorahCommentSource.RASHI_ALT
                        elif css_class_prefix == "ezra":
                            new_comment_source = TorahCommentSource.IBN_EZRA
                        else:
                            print(
                                "Ignoring element with unexpected css class prefix "
                                + f"for comment paragraph: {css_class_prefix} (from {child})"
                            )
                            continue

                        if (
                            anchor_phrase is not None
                            or current_comment_data is None
                            or new_comment_source != current_comment_source
                        ):  # new comment!
                            if current_comment_data is not None and current_comment_source is not None:
                                verse_data["comments"][current_comment_source].append(current_comment_data)

                            current_comment_data = CommentData(
                                anchor_phrase=anchor_phrase,
                                comment=comment_html,
                                format="html",
                            )
                            current_comment_source = new_comment_source
                        else:
                            current_comment_data["comment"] += "<br/>" + comment_html

                    if current_comment_data is not None and current_comment_source is not None:
                        verse_data["comments"][current_comment_source].append(current_comment_data)

                chapter_data["verses"].append(verse_data)
            if add_chapter_to_parsha:
                parsha_data["chapters"].append(chapter_data)

    try:
        merge_and_save_parsha_data(parsha, parsha_data)
    except Exception:
        Path(f"temp-lechaim-{parsha}.json").write_text(dump_parsha(parsha_data))
        raise


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("parsha_index", type=int)
    argparser.add_argument("parsha_url_path", type=str)
    argparser.add_argument("--allow-incomplete", action="store_true")
    args = argparser.parse_args()
    parse(args.parsha_index, args.parsha_url_path, allow_incomplete=bool(args.allow_incomplete))
