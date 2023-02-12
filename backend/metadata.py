from typing import Any


class TextSource:
    FG = "fg"
    PLAUT = "plaut"
    LECHAIM = "lechaim"
    HEBREW = "hebrew"

    @classmethod
    def all(cls) -> list[str]:
        return [cls.FG, cls.PLAUT, cls.LECHAIM, cls.HEBREW]

    @classmethod
    def validate_per_text_source_dict(cls, d: dict[str, Any]):
        if set(d.keys()) != set(cls.all()):
            raise SystemExit(f"Missing or extra records in per-text source dict {d}")


text_source_marks = {
    TextSource.FG: "[ФГ]",
    TextSource.PLAUT: "[Plaut]",
    TextSource.LECHAIM: "[Лехаим]",
    TextSource.HEBREW: "",
}


text_source_descriptions = {
    TextSource.FG: "Русский перевод Фримы Гурфинкель",
    TextSource.PLAUT: "Английский перевод «The Torah: A Modern Commentary» под редакцией Гюнтера Плаута",
    TextSource.LECHAIM: "Русский перевод Давида Сафронова под ред. Андрея Графова (изд. «Лехаим»)",
    TextSource.HEBREW: "Версия на иврите с огласовками (никуд)",
}


text_source_links = {
    TextSource.FG: [
        r"http://www.shabat-shalom.info/books/Tanach-ru/Chumash_Rashi/index.htm",
        r"http://www.ejwiki.org/wiki/%D0%93%D1%83%D1%80%D1%84%D0%B8%D0%BD%D0%BA%D0%B5%D0%BB%D1%8C,_%D0%A4%D1%80%D0%B8%D0%BC%D0%B0",  # noqa
        r"https://esxatos.com/gurfinel-tora-tanah-28-knig-1-fayl",
    ],
    TextSource.PLAUT: [
        r"https://reformjudaism.org/learning/torah-study/english-translations-torah-portions",
        r"https://www.ccarpress.org/shopping_product_detail.asp?pid=50297",
        r"https://www.ccarpress.org/content.asp?tid=532",
    ],
    TextSource.LECHAIM: [
        r"https://lechaim.ru/torah/",
        r"https://esxatos.com/tora-s-kommentariyami-rashi-v-5-tomah-knizhniki",
    ],
    TextSource.HEBREW: [
        r"https://www.sefaria.org/texts/Tanakh",
        r"https://en.wikipedia.org/wiki/Niqqud",
    ],
}


torah_book_names = {
    1: {
        TextSource.FG: "Берейшис",
        TextSource.PLAUT: "Genesis",
        TextSource.LECHAIM: "Берешит",
        TextSource.HEBREW: "בראשית",
    },
    2: {
        TextSource.FG: "Шемот",
        TextSource.PLAUT: "Exodus",
        TextSource.LECHAIM: "Шмот",
        TextSource.HEBREW: "שמות",
    },
    3: {
        TextSource.FG: "Вайикра",
        TextSource.PLAUT: "Leviticus",
        TextSource.LECHAIM: "Ваикра",
        TextSource.HEBREW: "ויקרא",
    },
    4: {
        TextSource.FG: "Бемидбар",
        TextSource.PLAUT: "Numbers",
        TextSource.LECHAIM: "Бемидбар",
        TextSource.HEBREW: "במדבר",
    },
    5: {
        TextSource.FG: "Деварим",
        TextSource.PLAUT: "Deuteronomy",
        TextSource.LECHAIM: "Дварим",
        TextSource.HEBREW: "דברים",
    },
}


torah_book_parsha_ranges: dict[int, tuple[int, int]] = {  # upper bound not included, as in list ranges
    1: (1, 13),
    2: (13, 24),
    3: (24, 34),
    4: (34, 44),
    5: (44, 55),
}


ChapterVerse = tuple[int, int]

chapter_verse_ranges: dict[int, tuple[ChapterVerse, ChapterVerse]] = {  # upper bound included
    1: ((1, 1), (6, 8)),
    2: ((6, 9), (11, 32)),
    3: ((12, 1), (17, 27)),
    4: ((18, 1), (22, 24)),
    5: ((23, 1), (25, 18)),
    6: ((25, 19), (28, 9)),
    7: ((28, 10), (32, 3)),
    8: ((32, 4), (36, 43)),
    9: ((37, 1), (40, 23)),
    10: ((41, 1), (44, 17)),
    11: ((44, 18), (47, 27)),
    12: ((47, 28), (50, 26)),
    # book break here, see torah_book_parsha_ranges
    13: ((1, 1), (6, 1)),
    14: ((6, 2), (9, 35)),
    15: ((10, 1), (13, 16)),
    16: ((13, 17), (17, 16)),
    17: ((18, 1), (20, 23)),
    18: ((21, 1), (24, 18)),
    19: ((25, 1), (27, 19)),
    20: ((27, 20), (30, 10)),
    21: ((30, 11), (34, 35)),
    22: ((35, 1), (38, 20)),
    23: ((38, 21), (40, 38)),
    # book break
    24: ((1, 1), (5, 26)),
    25: ((6, 1), (8, 36)),
    26: ((9, 1), (11, 47)),
    27: ((12, 1), (13, 59)),
    28: ((14, 1), (15, 33)),
    29: ((16, 1), (18, 30)),
    30: ((19, 1), (20, 27)),
    31: ((21, 1), (24, 23)),
    32: ((25, 1), (26, 2)),
    33: ((26, 3), (27, 34)),
    # book break
    34: ((1, 1), (4, 20)),
    35: ((4, 21), (7, 89)),
    36: ((8, 1), (12, 16)),
    37: ((13, 1), (15, 41)),
    38: ((16, 1), (18, 32)),
    39: ((19, 1), (22, 1)),
    40: ((22, 2), (25, 9)),
    41: ((25, 10), (30, 1)),
    42: ((30, 2), (32, 42)),
    43: ((33, 1), (36, 13)),
    # book break
    44: ((1, 1), (3, 22)),
    45: ((3, 23), (7, 11)),
    46: ((7, 12), (11, 25)),
    47: ((11, 26), (16, 17)),
    48: ((16, 18), (21, 9)),
    49: ((21, 10), (25, 19)),
    50: ((26, 1), (29, 8)),
    51: ((29, 9), (30, 20)),
    52: ((31, 1), (31, 30)),
    53: ((32, 1), (32, 52)),
    54: ((33, 1), (34, 12)),
}


def get_book_by_parsha(parsha: int) -> int:
    for book, parsha_range in torah_book_parsha_ranges.items():
        if parsha >= parsha_range[0] and parsha < parsha_range[1]:
            return book
    else:
        raise ValueError(f"No torah book found for parsha {parsha}")


parsha_names = {
    1: {
        TextSource.FG: "Берейшис",
        TextSource.PLAUT: "B’reishit (In the Beginning)",
        TextSource.LECHAIM: "Берешит",
        TextSource.HEBREW: "בראשית",
    },
    2: {
        TextSource.FG: "Нойах",
        TextSource.PLAUT: "Noach (Noah)",
        TextSource.LECHAIM: "Ноах",
        TextSource.HEBREW: "נח",
    },
    3: {
        TextSource.FG: "Лех Лехо",
        TextSource.PLAUT: "Lech L’cha (Go Forth)",
        TextSource.LECHAIM: "Лех-леха",
        TextSource.HEBREW: "לך לך",
    },
    4: {
        TextSource.FG: "Вайейро",
        TextSource.PLAUT: "Vayeira (I (God) Appeared [to Abraham, Isaac, and Jacob])",
        TextSource.LECHAIM: "Вайера",
        TextSource.HEBREW: "וירא",
    },
    5: {
        TextSource.FG: "Хайей Соро",
        TextSource.PLAUT: "Chayei Sarah (The Life of Sarah)",
        TextSource.LECHAIM: "Хайей сара",
        TextSource.HEBREW: "חיי שרה",
    },
    6: {
        TextSource.FG: "Толдойс",
        TextSource.PLAUT: "Tol’dot (The Generations [of Isaac])",
        TextSource.LECHAIM: "Тольдот",
        TextSource.HEBREW: "תולדות",
    },
    7: {
        TextSource.FG: "Вайейцей",
        TextSource.PLAUT: "Vayeitzei (And [Jacob] Left)",
        TextSource.LECHAIM: "Вайеце",
        TextSource.HEBREW: "ויצא",
    },
    8: {
        TextSource.FG: "Вайишлах",
        TextSource.PLAUT: "Vayishlach ([Jacob] Sent)",
        TextSource.LECHAIM: "Ваишлах",
        TextSource.HEBREW: "וישלח",
    },
    9: {
        TextSource.FG: "Вайейшев",
        TextSource.PLAUT: "Vayeishev ([Jacob] Settled)",
        TextSource.LECHAIM: "Вайешев",
        TextSource.HEBREW: "וישב",
    },
    10: {
        TextSource.FG: "Микец",
        TextSource.PLAUT: "Mikeitz (After [Two Years])",
        TextSource.LECHAIM: "Микец",
        TextSource.HEBREW: "מקץ",
    },
    11: {
        TextSource.FG: "Вайигаш",
        TextSource.PLAUT: "Vayigash (And [Judah] Approached [Joseph])",
        TextSource.LECHAIM: "Ваигаш",
        TextSource.HEBREW: "ויגש",
    },
    12: {
        TextSource.FG: "Вайхи",
        TextSource.PLAUT: "Va-y’chi ([Jacob] Lived)",
        TextSource.LECHAIM: "Вайехи",
        TextSource.HEBREW: "ויחי",
    },
    13: {
        TextSource.FG: "Шемойс",
        TextSource.PLAUT: "Sh’mot (Names)",
        TextSource.LECHAIM: "Шмот",
        TextSource.HEBREW: "שמות",
    },
    14: {
        TextSource.FG: "Воэйро",
        TextSource.PLAUT: "Va-eira (I (God) Appeared [to Abraham, Isaac, and Jacob])",
        TextSource.LECHAIM: "Ваэра",
        TextSource.HEBREW: "וארא",
    },
    15: {
        TextSource.FG: "Бой",
        TextSource.PLAUT: "Bo (Go [to Pharaoh])",
        TextSource.LECHAIM: "Бо",
        TextSource.HEBREW: "בא",
    },
    16: {
        TextSource.FG: "Бешалах",
        TextSource.PLAUT: "B’shalach (Now When [Pharaoh] Let [the People] Go)",
        TextSource.LECHAIM: "Бешалах",
        TextSource.HEBREW: "בשלח",
    },
    17: {
        TextSource.FG: "Йисрой",
        TextSource.PLAUT: "Yitro (Jethro)",
        TextSource.LECHAIM: "Итро",
        TextSource.HEBREW: "יתרו",
    },
    18: {
        TextSource.FG: "Мишпотим",
        TextSource.PLAUT: "Mishpatim ([These Are the] Rules)",
        TextSource.LECHAIM: "Мишпатим",
        TextSource.HEBREW: "משפטים",
    },
    19: {
        TextSource.FG: "Терумо",
        TextSource.PLAUT: "T’rumah (Gifts)",
        TextSource.LECHAIM: "Трума",
        TextSource.HEBREW: "תרומה",
    },
    20: {
        TextSource.FG: "Тецаве",
        TextSource.PLAUT: "T’tzaveh ([You] Shall Further Instruct)",
        TextSource.LECHAIM: "Тецаве",
        TextSource.HEBREW: "תצוה",
    },
    21: {
        TextSource.FG: "Тисо",
        TextSource.PLAUT: "Ki Tisa (When You Take a Census)",
        TextSource.LECHAIM: "Ки тиса",
        TextSource.HEBREW: "כי תשא",
    },
    22: {
        TextSource.FG: "Вайакгел",
        TextSource.PLAUT: "Vayak’heil ([Moses] Assembled)",
        TextSource.LECHAIM: "Ваякгель",
        TextSource.HEBREW: "ויקהל",
    },
    23: {
        TextSource.FG: "Пкудей",
        TextSource.PLAUT: "P’kudei ([The] Records [of the Tabernacle])",
        TextSource.LECHAIM: "Пекудей",
        TextSource.HEBREW: "פקודי",
    },
    24: {
        TextSource.FG: "Вайикро",
        TextSource.PLAUT: "Vayikra ([God] Called Out)",
        TextSource.LECHAIM: "Ваикра",
        TextSource.HEBREW: "ויקרא",
    },
    25: {
        TextSource.FG: "Цав",
        TextSource.PLAUT: "Tzav (Command [Aaron and His Sons])",
        TextSource.LECHAIM: "Цав",
        TextSource.HEBREW: "צו",
    },
    26: {
        TextSource.FG: "Шмини",
        TextSource.PLAUT: "Sh’mini (The Eighth [Day])",
        TextSource.LECHAIM: "Шмини",
        TextSource.HEBREW: "שמיני",
    },
    27: {
        TextSource.FG: "Тазриа",
        TextSource.PLAUT: "Tazria (Bearing Seed)",
        TextSource.LECHAIM: "Тазриа",
        TextSource.HEBREW: "תזריע",
    },
    28: {
        TextSource.FG: "Мецойро",
        TextSource.PLAUT: "M’tzor (A Leper)",
        TextSource.LECHAIM: "Мецора",
        TextSource.HEBREW: "מצורע",
    },
    29: {
        TextSource.FG: "Ахарей",
        TextSource.PLAUT: "Acharei Mot (After the Death [of the Two Sons of Aaron])",
        TextSource.LECHAIM: "Ахарей мот",
        TextSource.HEBREW: "אחרי מות",
    },
    30: {
        TextSource.FG: "Кдойшим",
        TextSource.PLAUT: "K’doshim ([You Shall Be] Holy)",
        TextSource.LECHAIM: "Кдошим",
        TextSource.HEBREW: "קדושים",
    },
    31: {
        TextSource.FG: "Эмойр",
        TextSource.PLAUT: "Emor (Speak)",
        TextSource.LECHAIM: "Эмор",
        TextSource.HEBREW: "אמור",
    },
    32: {
        TextSource.FG: "Бегар",
        TextSource.PLAUT: "B’har (On Mount [Sinai])",
        TextSource.LECHAIM: "Бегар",
        TextSource.HEBREW: "בהר",
    },
    33: {
        TextSource.FG: "Бехукойсай",
        TextSource.PLAUT: "B’chukotai (My Laws)",
        TextSource.LECHAIM: "Бехукотай",
        TextSource.HEBREW: "בחוקתי",
    },
    34: {
        TextSource.FG: "Бемидбар",
        TextSource.PLAUT: "B’midbar (In the Wilderness)",
        TextSource.LECHAIM: "Бемидбар",
        TextSource.HEBREW: "במדבר",
    },
    35: {
        TextSource.FG: "Носой",
        TextSource.PLAUT: "Naso (Take a Census)",
        TextSource.LECHAIM: "Насо",
        TextSource.HEBREW: "נשא",
    },
    36: {
        TextSource.FG: "Бегаалойсхо",
        TextSource.PLAUT: "B’haalot’cha (When You Raise [the Lamps])",
        TextSource.LECHAIM: "Бегаалотха",
        TextSource.HEBREW: "בהעלותך",
    },
    37: {
        TextSource.FG: "Шлах",
        TextSource.PLAUT: "Sh’lach L’cha (Send [Notables to Scout the Land])",
        TextSource.LECHAIM: "Шлах",
        TextSource.HEBREW: "שלח",
    },
    38: {
        TextSource.FG: "Койрах",
        TextSource.PLAUT: "Korach (Korach)",
        TextSource.LECHAIM: "Корах",
        TextSource.HEBREW: "קרח",
    },
    39: {
        TextSource.FG: "Хукас",
        TextSource.PLAUT: "Chukat (The Ritual Law)",
        TextSource.LECHAIM: "Хукат",
        TextSource.HEBREW: "חקת",
    },
    40: {
        TextSource.FG: "Болок",
        TextSource.PLAUT: "Balak (Balak)",
        TextSource.LECHAIM: "Балак",
        TextSource.HEBREW: "בלק",
    },
    41: {
        TextSource.FG: "Пинхас",
        TextSource.PLAUT: "Pinchas (Phinehas)",
        TextSource.LECHAIM: "Пинхас",
        TextSource.HEBREW: "פנחס",
    },
    42: {
        TextSource.FG: "Матойс",
        TextSource.PLAUT: "Matot (Tribes)",
        TextSource.LECHAIM: "Матот",
        TextSource.HEBREW: "מטות",
    },
    43: {
        TextSource.FG: "Масэй",
        TextSource.PLAUT: "Mas-ei (The Marches)",
        TextSource.LECHAIM: "Масеэй",
        TextSource.HEBREW: "מסעי",
    },
    44: {
        TextSource.FG: "Деворим",
        TextSource.PLAUT: "D’varim (The Words)",
        TextSource.LECHAIM: "Дварим",
        TextSource.HEBREW: "דברים",
    },
    45: {
        TextSource.FG: "Воэсханан",
        TextSource.PLAUT: "Va-et’chanan (I [Moses] Pleaded with the Eternal)",
        TextSource.LECHAIM: "Ваэтханан",
        TextSource.HEBREW: "ואתחנן",
    },
    46: {
        TextSource.FG: "Экев",
        TextSource.PLAUT: "Eikev ([And if You] Obey [These Rules])",
        TextSource.LECHAIM: "Экев",
        TextSource.HEBREW: "עקב",
    },
    47: {
        TextSource.FG: "Рээй",
        TextSource.PLAUT: "R’eih (See [This Day I Set Before You Blessing and Curse])",
        TextSource.LECHAIM: "Реэ",
        TextSource.HEBREW: "ראה",
    },
    48: {
        TextSource.FG: "Шойфтим",
        TextSource.PLAUT: "Shof’tim (Judges)",
        TextSource.LECHAIM: "Шофтим",
        TextSource.HEBREW: "שופטים",
    },
    49: {
        TextSource.FG: "Ки Тейцей",
        TextSource.PLAUT: "Ki’Teitzei (When You Go Out (to Battle))",
        TextSource.LECHAIM: "Ки теце",
        TextSource.HEBREW: "כי תצא",
    },
    50: {
        TextSource.FG: "Ки Совой",
        TextSource.PLAUT: "Ki Tavo (When You Enter [the Land])",
        TextSource.LECHAIM: "Ки таво",
        TextSource.HEBREW: "כי תבוא",
    },
    51: {
        TextSource.FG: "Ницовим",
        TextSource.PLAUT: "Nitzavim (You Stand [This Day])",
        TextSource.LECHAIM: "Ницавим",
        TextSource.HEBREW: "נצבים",
    },
    52: {
        TextSource.FG: "Вайейлех",
        TextSource.PLAUT: "Vayeilech ([Moses] Went)",
        TextSource.LECHAIM: "Вайелех",
        TextSource.HEBREW: "וילך",
    },
    53: {
        TextSource.FG: "Гаазину",
        TextSource.PLAUT: "Haazinu (Listen)",
        TextSource.LECHAIM: "Гаазину",
        TextSource.HEBREW: "האזינו",
    },
    54: {
        TextSource.FG: "Везойс гаБрохо",
        TextSource.PLAUT: "V’zot Hab’rachah (And This is the Blessing)",
        TextSource.LECHAIM: "Везот га-браха",
        TextSource.HEBREW: "וזאת הברכה",
    },
}


TextSource.validate_per_text_source_dict(text_source_marks)
TextSource.validate_per_text_source_dict(text_source_links)
TextSource.validate_per_text_source_dict(text_source_descriptions)
for _, names in torah_book_names.items():
    TextSource.validate_per_text_source_dict(names)
for _, names in parsha_names.items():
    TextSource.validate_per_text_source_dict(names)


class Commenter:
    SONCHINO = "sonchino"
    RASHI = "rashi"
    RASHI_ALT = "rashi_alt"
    IBN_EZRA = "ibn-ezra"
    RAMBAN = "ramban"
    OR_HACHAIM = "or_hachaim"


commenter_names = {
    Commenter.SONCHINO: "Сончино [ФГ]",
    Commenter.RASHI: "Раши [ФГ]",
    Commenter.RASHI_ALT: "Раши [Лехаим]",
    Commenter.IBN_EZRA: "ибн Эзра [Лехаим]",
    Commenter.RAMBAN: "Рамбан [Chavel]",
    Commenter.OR_HACHAIM: "Ор ха-Хайим [Munk]",
}


commenter_links = {
    Commenter.SONCHINO: [
        r"https://toldot.com/Sonchino.html",
        r"https://ru.wikipedia.org/wiki/%D0%93%D0%B5%D1%80%D1%86,_%D0%99%D0%BE%D1%81%D0%B5%D1%84_%D0%A6%D0%B2%D0%B8",
    ],
    Commenter.RASHI: [
        r"https://toldot.com/TorahRashi.html",
        r"https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D1%88%D0%B8",
    ],
    Commenter.RASHI_ALT: [],
    Commenter.IBN_EZRA: [
        r"https://toldot.com/ibnEzra.html",
        r"https://ru.wikipedia.org/wiki/%D0%90%D0%B2%D1%80%D0%B0%D0%B0%D0%BC_%D0%B8%D0%B1%D0%BD_%D0%AD%D0%B7%D1%80%D0%B0",  # noqa
    ],
    Commenter.RAMBAN: [
        r"https://en.wikipedia.org/wiki/Nachmanides",
        r"https://www.sefaria.org/texts/Tanakh/Rishonim%20on%20Tanakh/Ramban/Torah",
        r"https://www.nli.org.il/he/books/NNL_ALEPH002108945/NLI",
    ],
    Commenter.OR_HACHAIM: [
        r"https://en.wikipedia.org/wiki/Chaim_ibn_Attar",
        r"https://www.sefaria.org/texts/Tanakh/Acharonim%20on%20Tanakh/Or%20HaChaim/Torah",
        r"https://mysefer.com/Or-HaChaim--Commentary-on-the-Torah-English-5-vol.__p-946.aspx",
        r"https://www.nehora.com/or-hachaim-commentary-on-the-torah/",
    ],
}
