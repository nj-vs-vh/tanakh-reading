import argparse
from pathlib import Path

import bs4  # type: ignore
import requests  # type: ignore

SCRIPT_DIR = Path(__file__).parent
HTML_DIR = SCRIPT_DIR / "../../html/neviim/mrk"

HTML_DIR.mkdir(parents=True, exist_ok=True)


def parse_book(idx: int, urlname: str):
    file = HTML_DIR / f"{idx}.html"
    if not file.exists():
        resp = requests.get(f"https://toraonline.ru/neviim/{urlname}.htm")
        resp.encoding = "windows-1251"  # wtf is wrong with you
        print(resp)
        file.write_text(resp.text)
    soup = bs4.BeautifulSoup(markup=file.read_text(), features="html.parser")
    for chapter_header in soup.find_all("h3"):
        chapter_header: bs4.Tag  # type: ignore
        print(chapter_header)
        chapter_paragraph = chapter_header.find_next_sibling("p")
        print(chapter_paragraph)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("book_idx", type=int)
    argparser.add_argument("book_url_name", type=str)
    args = argparser.parse_args()

    parse_book(args.book_idx, args.book_url_name)
