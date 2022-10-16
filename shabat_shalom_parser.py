"""Parser for http://www.shabat-shalom.info/books/Tanach-ru/"""

import argparse
import copy
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

import bs4
import requests  # type: ignore

import metadata
from metadata import Commenter, Translation
from model import ChapterData, CommentData, ParshaData, VerseData
from utils import (
    are_strings_close,
    collapse_whitespace,
    has_class,
    inner_tag_text,
    postprocess_patched_text,
    strip_html_breaks,
    strip_leading_dot,
)


def parsha_html(idx: int) -> Path:
    return Path(f"html/shabat_shalom_info/{idx}.html")


def download_parsha_html(idx: int):
    target_file = parsha_html(idx)
    if target_file.exists():
        print(f"Parsha #{idx} already downloaded")
        return
    print(f"Downloading parsha #{idx}")
    url = f"http://www.shabat-shalom.info/books/Tanach-ru/Chumash_Rashi/{idx}.htm"
    print(f"URL = {url}")
    resp = requests.get(url)
    if resp.status_code != 200:
        print(resp.text)
        raise RuntimeError()
    target_file.write_bytes(resp.content)
    print("Done!")


def parse_parsha(parsha: int):
    book: Optional[int] = None
    for book_no, parsha_range in metadata.torah_book_parsha_ranges.items():
        if parsha >= parsha_range[0] and parsha < parsha_range[1]:
            book = book_no
            break
    if book is None:
        raise ValueError(f"No torah book found for parsha {parsha}")

    parsha_data = ParshaData(
        book=book,
        parsha=parsha,
        chapters=[],
    )

    print(
        f"Parsing shabat-shalom.info for book {metadata.torah_book_names[book][Translation.FG]!r}, "
        + f"parsha {metadata.parsha_names[parsha][Translation.FG]!r}"
    )

    html = parsha_html(parsha)
    download_parsha_html(parsha)

    bs = bs4.BeautifulSoup(html.read_text(), features="html.parser")

    main_content = bs.find("div", attrs={"class": "chumash_text"})
    chapter_anchors: bs4.ResultSet[bs4.Tag] = main_content.find_all("a")
    chapter_anchors = [a for a in chapter_anchors if a.attrs.get("name", "").startswith("p")]

    def chapter_from_anchor(a: bs4.Tag) -> int:
        return int(a.attrs["name"].lstrip("p"))

    chapters = [chapter_from_anchor(a) for a in chapter_anchors]
    min_chapter = min(chapters)
    max_chapter = max(chapters)
    expected_chapters = list(range(min_chapter, max_chapter + 1))
    if chapters != expected_chapters:
        raise RuntimeError(
            f"Something is wrong with parsed chapter list: {chapters} differs from expected {expected_chapters}"
        )
    print(f"Chapters from {min_chapter} to {max_chapter} (inclusive)")

    current_chapter_data: Optional[ChapterData] = None
    current_verse_data: Optional[VerseData] = None
    for child in main_content.children:
        if child in chapter_anchors:
            # new chapter is prepended with the <a name="p11"/> anchor
            if current_chapter_data is not None:
                if current_verse_data is not None:
                    current_chapter_data["verses"].append(current_verse_data)
                    current_verse_data = None
            current_chapter_data = ChapterData(chapter=chapter_from_anchor(child), verses=[])
            parsha_data["chapters"].append(current_chapter_data)
            expected_next_verse = 1
            continue
        if current_chapter_data is None:
            continue

        def parse_rashi_comment_from_ref_el(el: bs4.Tag):
            """Rashi comments may include nested comments, so the recursive function is needed"""
            if has_class(el, "rashi"):
                return

            if not has_class(el, "rashi_ref") and isinstance(el, bs4.Tag):
                rashi_ref_descendants = [el_d for el_d in el.descendants if has_class(el_d, "rashi_ref")]
                if rashi_ref_descendants:
                    el = rashi_ref_descendants[0]

            if has_class(el, "rashi_ref"):
                if "id" not in el.attrs:
                    print(f"WARNING: Rashi ref element without id: {el}")
                    return
                comment_id = el.attrs["id"].removeprefix("_commentref")
                comment_span = main_content.find("span", attrs={"id": "_comment" + comment_id})
                if comment_span is None:
                    print(f"WARNING: Rashi comment not found for ref {el}")
                comment_text_html = ""
                anchor_phrase = inner_tag_text(el)
                for comment_span_child in comment_span.children:
                    parse_rashi_comment_from_ref_el(comment_span_child)
                    if has_class(comment_span_child, "rashi"):
                        continue
                    if isinstance(comment_span_child, bs4.Tag):
                        if not inner_tag_text(comment_span_child):
                            continue
                        if comment_span_child.name == "b" and are_strings_close(
                            inner_tag_text(comment_span_child), anchor_phrase
                        ):
                            continue
                        if inner_tag_text(comment_span_child) == "(Раши)":
                            continue
                    comment_text_html += " " + collapse_whitespace(str(comment_span_child))
                if current_verse_data is not None:
                    current_verse_data["comments"][Commenter.RASHI].append(
                        CommentData(
                            anchor_phrase=anchor_phrase,
                            comment=strip_leading_dot(postprocess_patched_text(strip_html_breaks(comment_text_html))),
                            format="html",
                        )
                    )

        if isinstance(child, bs4.Tag):
            if has_class(child, "rashi") or has_class(child, "sonch"):
                # actual comment spans are skipped, we find them later by ids
                continue
            if has_class(child, "rashi_ref"):
                parse_rashi_comment_from_ref_el(child)
            if has_class(child, "comment_handle"):
                # sonchino comment parsing
                comment_id = child.attrs["id"].removeprefix("_commentref")
                comment_span = main_content.find("span", attrs={"id": "_comment" + comment_id})
                # one span can contain several comments
                sonchino_comments: list[CommentData] = []
                current_comment_data: Optional[CommentData] = None
                for comment_span_child in comment_span.children:
                    if isinstance(comment_span_child, bs4.Tag) and comment_span_child.name == "b":
                        if current_comment_data is not None:
                            sonchino_comments.append(current_comment_data)
                        current_comment_data = CommentData(
                            anchor_phrase=inner_tag_text(comment_span_child),
                            comment="",
                            format="html",
                        )
                    else:
                        if current_comment_data is not None:
                            if inner_tag_text(comment_span_child) != "(Сончино)":
                                current_comment_data["comment"] += " " + collapse_whitespace(str(comment_span_child))
                        elif inner_tag_text(comment_span_child):
                            current_comment_data = CommentData(
                                anchor_phrase=None,
                                comment=str(comment_span_child),
                                format="html",
                            )
                if current_comment_data is not None:
                    sonchino_comments.append(current_comment_data)

                for comment_data in sonchino_comments:
                    comment_data["comment"] = strip_html_breaks(comment_data["comment"])

                if current_verse_data is not None:
                    current_verse_data["comments"][Commenter.SONCHINO] = sonchino_comments

                # the actual handle is not inserted in the final text
                continue

        text_part = inner_tag_text(child)
        if not text_part or text_part.startswith("Глава"):  # skipping chapter header and whitespace
            continue

        def verse_prefix(no: int) -> str:
            return f"{no}."

        def split_on_next_verse_start(s: str, next_verse: int) -> tuple[str, Optional[str]]:
            try:
                next_verse_start_match = next(re.finditer(re.escape(verse_prefix(next_verse)), s))
                next_verse_start_start = next_verse_start_match.start()
                return text_part[:next_verse_start_start], text_part[next_verse_start_start:]
            except StopIteration:
                return text_part, None

        text_part_current_verse, text_part_next_verse = split_on_next_verse_start(text_part, expected_next_verse)

        if current_verse_data is not None:
            current_verse_data["text"][Translation.FG] += " " + text_part_current_verse

        while text_part_next_verse is not None:
            if current_verse_data is not None:
                current_verse_data["text"][Translation.FG] = postprocess_patched_text(
                    current_verse_data["text"][Translation.FG]
                )
                current_chapter_data["verses"].append(current_verse_data)
            current_verse = expected_next_verse
            text_part = text_part_next_verse.removeprefix(verse_prefix(current_verse)).strip()
            expected_next_verse += 1
            text_part_current_verse, text_part_next_verse = split_on_next_verse_start(text_part, expected_next_verse)
            current_verse_data = VerseData(
                verse=current_verse,
                text={Translation.FG: text_part_current_verse},
                comments=defaultdict(list),
            )

    print("Validating parsed data")
    parsed_chapters = [c["chapter"] for c in parsha_data["chapters"]]

    if parsed_chapters != list(range(min_chapter, max_chapter + 1)):
        print(f"WARNING: parsed chapters {parsed_chapters} do not match the expected {expected_chapters}")
    for chapter_data in parsha_data["chapters"]:
        for verse_data in chapter_data["verses"]:
            if not verse_data["text"]:
                print(f"WARNING: missing translation for chapter {chapter_data['chapter']} verse {verse_data['verse']}")
        verses = [v["verse"] for v in chapter_data["verses"]]
        if verses != list(range(min(verses), max(verses) + 1)):
            print(f"WARNING: there are some missing verses in chapter {chapter_data['chapter']}: {verses}")

    Path(f"json/{parsha}.json").write_text(json.dumps(parsha_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("parsha_index", type=int)
    args = argparser.parse_args()
    parse_parsha(args.parsha_index)
