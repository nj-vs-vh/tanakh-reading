import re

parsha_listing = """
Joshua 1–11
Joshua 12–19
Joshua 20–24
Judges 1–11
Judges 12–21
I Samuel 1–8
I Samuel 9–13
I Samuel 14–25
I Samuel 26–31
II Samuel 1–7
II Samuel 8–18
II Samuel 19–24
I Kings 1–6
I Kings 7–10
I Kings 11–19
I Kings 20–22
II Kings 1–5
II Kings 6–12
II Kings 13–18
II Kings 19–25
Jeremiah 1–8
Jeremiah 9–17
Jeremiah 18–31
Jeremiah 32–37
Jeremiah 38–48
Jeremiah 49–52
Ezekiel 1–9
Ezekiel 10–17
Ezekiel 18–22
Ezekiel 23–27
Ezekiel 28–30
Ezekiel 31–40
Ezekiel 41–43
Ezekiel 44–46
Ezekiel 47–48
Isaiah 1–5
Isaiah 6–9
Isaiah 10–13
Isaiah 14–20
Isaiah 21–24
Isaiah 25–29
Isaiah 30–33
Isaiah 34–40
Isaiah 41–44
Isaiah 45–49
Isaiah 50–58
Isaiah 59–66
Hosea 1–6
Hosea 7–12
Hosea 13–14
Joel 1–4
Amos 1–9
Obadiah 1–1
Jonah 1–4
Micah 1–7
Nahum 1–3
Habakkuk 1–3
Zephaniah 1–3
Haggai 1–2
Zechariah 1–11
Zechariah 12–14
Malachi 1–3
"""

translations = {
    "Joshua": "Йеhошуа",
    "Judges": "Шойфтим",
    "I Samuel": "Шемуэйл I",
    "II Samuel": "Шемуэйл II",
    "I Kings": "Мелахим I",
    "II Kings": "Мелахим II",
    "Isaiah": "Йешайа",
    "Jeremiah": "Йирмейа",
    "Ezekiel": "Йехэзкэйл",
    "Hosea": "Ошеа",
    "Joel": "Йоель",
    "Amos": "Амос",
    "Obadiah": "Овадья",
    "Jonah": "Йона",
    "Micah": "Миха",
    "Nahum": "Нахум",
    "Habakkuk": "Хавакук",
    "Zephaniah": "Цфанья",
    "Haggai": "Хагай",
    "Zechariah": "Зехарья",
    "Malachi": "Малахи",
}


book_order = [
    "Joshua",
    "Judges",
    "I Samuel",
    "II Samuel",
    "I Kings",
    "II Kings",
    "Jeremiah",
    "Ezekiel",
    "Isaiah",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
]


code = []
for parsha_idx, parsha in enumerate(parsha_listing.strip().splitlines()):
    match_ = re.match(r"(.+?) (\d+)–(end|\d+)", parsha)
    if match_ is None:
        raise ValueError(parsha)
    book_name_eng = match_.group(1)
    book_id = 6 + book_order.index(book_name_eng)
    parsha_id = 55 + parsha_idx
    book_name_ru = translations[book_name_eng]
    start_chapter = match_.group(2)
    end_chapter = match_.group(3)
    parsha_urlname = (
        f"{book_name_eng}-{start_chapter}-{end_chapter}".replace("II", "second")
        .replace("I", "first")
        .lower()
        .replace(" ", "-")
    )
    to_end_chapter_ru = f"{end_chapter}" if end_chapter != "end" else "до конца"
    parsha_name_ru = f"{book_name_ru} {start_chapter}–{to_end_chapter_ru}"
    # print(book_id, parsha_id, eng_name, ru_name, start_chapter, end_chapter, sep=" | ")
    code.append(
        f"""
        ParshaInfo(
            id={parsha_id},
            book_id={book_id},
            chapter_verse_start=({start_chapter}, 1),
            chapter_verse_end=({end_chapter}, 0),
            name={{MRK_SOURCE: "{parsha_name_ru}"}},
            url_name="{parsha_urlname}",
        ),
    """.strip()
    )

print("\n".join(code))
print("\n\n")

code = []
for book_idx, book in enumerate(book_order):
    book_name_ru = translations[book]
    code.append(f'TanakhBookInfo(id={6 + book_idx}, name={{MRK_SOURCE: "{book_name_ru}"}}),')

print("\n".join(code))
