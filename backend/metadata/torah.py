from typing import Any

from backend.metadata.types import CommentSource as CommentSourceInfo
from backend.metadata.types import (
    IsoLang,
    ParshaInfo,
    TanakhBookInfo,
    TanakhSectionMetadata,
)
from backend.metadata.types import TextSource as TextSourceInfo


class TorahTextSource:
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
    TorahTextSource.FG: "[ФГ]",
    TorahTextSource.PLAUT: "[Plaut]",
    TorahTextSource.LECHAIM: "[Лехаим]",
    TorahTextSource.HEBREW: "[אָ]",
}


text_source_descriptions = {
    TorahTextSource.FG: "Русский перевод Фримы Гурфинкель",
    TorahTextSource.PLAUT: "Английский перевод «The Torah: A Modern Commentary» под редакцией Гюнтера Плаута",
    TorahTextSource.LECHAIM: "Русский перевод Давида Сафронова под ред. Андрея Графова (изд. «Лехаим»)",
    TorahTextSource.HEBREW: "Версия на иврите с огласовками (никуд)",
}


text_source_links = {
    TorahTextSource.FG: [
        r"http://www.shabat-shalom.info/books/Tanach-ru/Chumash_Rashi/index.htm",
        r"http://www.ejwiki.org/wiki/%D0%93%D1%83%D1%80%D1%84%D0%B8%D0%BD%D0%BA%D0%B5%D0%BB%D1%8C,_%D0%A4%D1%80%D0%B8%D0%BC%D0%B0",  # noqa
        r"https://esxatos.com/gurfinel-tora-tanah-28-knig-1-fayl",
    ],
    TorahTextSource.PLAUT: [
        r"https://reformjudaism.org/learning/torah-study/english-translations-torah-portions",
        r"https://www.ccarpress.org/shopping_product_detail.asp?pid=50297",
        r"https://www.ccarpress.org/content.asp?tid=532",
    ],
    TorahTextSource.LECHAIM: [
        r"https://lechaim.ru/torah/",
        r"https://esxatos.com/tora-s-kommentariyami-rashi-v-5-tomah-knizhniki",
    ],
    TorahTextSource.HEBREW: [
        r"https://www.sefaria.org/texts/Tanakh",
        r"https://en.wikipedia.org/wiki/Niqqud",
    ],
}


torah_book_names = {
    1: {
        TorahTextSource.FG: "Берейшис",
        TorahTextSource.PLAUT: "Genesis",
        TorahTextSource.LECHAIM: "Берешит",
        TorahTextSource.HEBREW: "בראשית",
    },
    2: {
        TorahTextSource.FG: "Шемот",
        TorahTextSource.PLAUT: "Exodus",
        TorahTextSource.LECHAIM: "Шмот",
        TorahTextSource.HEBREW: "שמות",
    },
    3: {
        TorahTextSource.FG: "Вайикра",
        TorahTextSource.PLAUT: "Leviticus",
        TorahTextSource.LECHAIM: "Ваикра",
        TorahTextSource.HEBREW: "ויקרא",
    },
    4: {
        TorahTextSource.FG: "Бемидбар",
        TorahTextSource.PLAUT: "Numbers",
        TorahTextSource.LECHAIM: "Бемидбар",
        TorahTextSource.HEBREW: "במדבר",
    },
    5: {
        TorahTextSource.FG: "Деварим",
        TorahTextSource.PLAUT: "Deuteronomy",
        TorahTextSource.LECHAIM: "Дварим",
        TorahTextSource.HEBREW: "דברים",
    },
}


text_source_languages: dict[str, IsoLang] = {
    TorahTextSource.FG: IsoLang.RU,
    TorahTextSource.PLAUT: IsoLang.EN,
    TorahTextSource.LECHAIM: IsoLang.RU,
    TorahTextSource.HEBREW: IsoLang.HE,
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


parsha_names = {
    1: {
        TorahTextSource.FG: "Берейшис",
        TorahTextSource.PLAUT: "B’reishit (In the Beginning)",
        TorahTextSource.LECHAIM: "Берешит",
        TorahTextSource.HEBREW: "בראשית",
    },
    2: {
        TorahTextSource.FG: "Нойах",
        TorahTextSource.PLAUT: "Noach (Noah)",
        TorahTextSource.LECHAIM: "Ноах",
        TorahTextSource.HEBREW: "נח",
    },
    3: {
        TorahTextSource.FG: "Лех Лехо",
        TorahTextSource.PLAUT: "Lech L’cha (Go Forth)",
        TorahTextSource.LECHAIM: "Лех-леха",
        TorahTextSource.HEBREW: "לך לך",
    },
    4: {
        TorahTextSource.FG: "Вайейро",
        TorahTextSource.PLAUT: "Vayeira (I (God) Appeared [to Abraham, Isaac, and Jacob])",
        TorahTextSource.LECHAIM: "Вайера",
        TorahTextSource.HEBREW: "וירא",
    },
    5: {
        TorahTextSource.FG: "Хайей Соро",
        TorahTextSource.PLAUT: "Chayei Sarah (The Life of Sarah)",
        TorahTextSource.LECHAIM: "Хайей сара",
        TorahTextSource.HEBREW: "חיי שרה",
    },
    6: {
        TorahTextSource.FG: "Толдойс",
        TorahTextSource.PLAUT: "Tol’dot (The Generations [of Isaac])",
        TorahTextSource.LECHAIM: "Тольдот",
        TorahTextSource.HEBREW: "תולדות",
    },
    7: {
        TorahTextSource.FG: "Вайейцей",
        TorahTextSource.PLAUT: "Vayeitzei (And [Jacob] Left)",
        TorahTextSource.LECHAIM: "Вайеце",
        TorahTextSource.HEBREW: "ויצא",
    },
    8: {
        TorahTextSource.FG: "Вайишлах",
        TorahTextSource.PLAUT: "Vayishlach ([Jacob] Sent)",
        TorahTextSource.LECHAIM: "Ваишлах",
        TorahTextSource.HEBREW: "וישלח",
    },
    9: {
        TorahTextSource.FG: "Вайейшев",
        TorahTextSource.PLAUT: "Vayeishev ([Jacob] Settled)",
        TorahTextSource.LECHAIM: "Вайешев",
        TorahTextSource.HEBREW: "וישב",
    },
    10: {
        TorahTextSource.FG: "Микец",
        TorahTextSource.PLAUT: "Mikeitz (After [Two Years])",
        TorahTextSource.LECHAIM: "Микец",
        TorahTextSource.HEBREW: "מקץ",
    },
    11: {
        TorahTextSource.FG: "Вайигаш",
        TorahTextSource.PLAUT: "Vayigash (And [Judah] Approached [Joseph])",
        TorahTextSource.LECHAIM: "Ваигаш",
        TorahTextSource.HEBREW: "ויגש",
    },
    12: {
        TorahTextSource.FG: "Вайхи",
        TorahTextSource.PLAUT: "Va-y’chi ([Jacob] Lived)",
        TorahTextSource.LECHAIM: "Вайехи",
        TorahTextSource.HEBREW: "ויחי",
    },
    13: {
        TorahTextSource.FG: "Шемойс",
        TorahTextSource.PLAUT: "Sh’mot (Names)",
        TorahTextSource.LECHAIM: "Шмот",
        TorahTextSource.HEBREW: "שמות",
    },
    14: {
        TorahTextSource.FG: "Воэйро",
        TorahTextSource.PLAUT: "Va-eira (I (God) Appeared [to Abraham, Isaac, and Jacob])",
        TorahTextSource.LECHAIM: "Ваэра",
        TorahTextSource.HEBREW: "וארא",
    },
    15: {
        TorahTextSource.FG: "Бой",
        TorahTextSource.PLAUT: "Bo (Go [to Pharaoh])",
        TorahTextSource.LECHAIM: "Бо",
        TorahTextSource.HEBREW: "בא",
    },
    16: {
        TorahTextSource.FG: "Бешалах",
        TorahTextSource.PLAUT: "B’shalach (Now When [Pharaoh] Let [the People] Go)",
        TorahTextSource.LECHAIM: "Бешалах",
        TorahTextSource.HEBREW: "בשלח",
    },
    17: {
        TorahTextSource.FG: "Йисрой",
        TorahTextSource.PLAUT: "Yitro (Jethro)",
        TorahTextSource.LECHAIM: "Итро",
        TorahTextSource.HEBREW: "יתרו",
    },
    18: {
        TorahTextSource.FG: "Мишпотим",
        TorahTextSource.PLAUT: "Mishpatim ([These Are the] Rules)",
        TorahTextSource.LECHAIM: "Мишпатим",
        TorahTextSource.HEBREW: "משפטים",
    },
    19: {
        TorahTextSource.FG: "Терумо",
        TorahTextSource.PLAUT: "T’rumah (Gifts)",
        TorahTextSource.LECHAIM: "Трума",
        TorahTextSource.HEBREW: "תרומה",
    },
    20: {
        TorahTextSource.FG: "Тецаве",
        TorahTextSource.PLAUT: "T’tzaveh ([You] Shall Further Instruct)",
        TorahTextSource.LECHAIM: "Тецаве",
        TorahTextSource.HEBREW: "תצוה",
    },
    21: {
        TorahTextSource.FG: "Тисо",
        TorahTextSource.PLAUT: "Ki Tisa (When You Take a Census)",
        TorahTextSource.LECHAIM: "Ки тиса",
        TorahTextSource.HEBREW: "כי תשא",
    },
    22: {
        TorahTextSource.FG: "Вайакгел",
        TorahTextSource.PLAUT: "Vayak’heil ([Moses] Assembled)",
        TorahTextSource.LECHAIM: "Ваякгель",
        TorahTextSource.HEBREW: "ויקהל",
    },
    23: {
        TorahTextSource.FG: "Пкудей",
        TorahTextSource.PLAUT: "P’kudei ([The] Records [of the Tabernacle])",
        TorahTextSource.LECHAIM: "Пекудей",
        TorahTextSource.HEBREW: "פקודי",
    },
    24: {
        TorahTextSource.FG: "Вайикро",
        TorahTextSource.PLAUT: "Vayikra ([God] Called Out)",
        TorahTextSource.LECHAIM: "Ваикра",
        TorahTextSource.HEBREW: "ויקרא",
    },
    25: {
        TorahTextSource.FG: "Цав",
        TorahTextSource.PLAUT: "Tzav (Command [Aaron and His Sons])",
        TorahTextSource.LECHAIM: "Цав",
        TorahTextSource.HEBREW: "צו",
    },
    26: {
        TorahTextSource.FG: "Шмини",
        TorahTextSource.PLAUT: "Sh’mini (The Eighth [Day])",
        TorahTextSource.LECHAIM: "Шмини",
        TorahTextSource.HEBREW: "שמיני",
    },
    27: {
        TorahTextSource.FG: "Тазриа",
        TorahTextSource.PLAUT: "Tazria (Bearing Seed)",
        TorahTextSource.LECHAIM: "Тазриа",
        TorahTextSource.HEBREW: "תזריע",
    },
    28: {
        TorahTextSource.FG: "Мецойро",
        TorahTextSource.PLAUT: "M’tzor (A Leper)",
        TorahTextSource.LECHAIM: "Мецора",
        TorahTextSource.HEBREW: "מצורע",
    },
    29: {
        TorahTextSource.FG: "Ахарей",
        TorahTextSource.PLAUT: "Acharei Mot (After the Death [of the Two Sons of Aaron])",
        TorahTextSource.LECHAIM: "Ахарей мот",
        TorahTextSource.HEBREW: "אחרי מות",
    },
    30: {
        TorahTextSource.FG: "Кдойшим",
        TorahTextSource.PLAUT: "K’doshim ([You Shall Be] Holy)",
        TorahTextSource.LECHAIM: "Кдошим",
        TorahTextSource.HEBREW: "קדושים",
    },
    31: {
        TorahTextSource.FG: "Эмойр",
        TorahTextSource.PLAUT: "Emor (Speak)",
        TorahTextSource.LECHAIM: "Эмор",
        TorahTextSource.HEBREW: "אמור",
    },
    32: {
        TorahTextSource.FG: "Бегар",
        TorahTextSource.PLAUT: "B’har (On Mount [Sinai])",
        TorahTextSource.LECHAIM: "Бегар",
        TorahTextSource.HEBREW: "בהר",
    },
    33: {
        TorahTextSource.FG: "Бехукойсай",
        TorahTextSource.PLAUT: "B’chukotai (My Laws)",
        TorahTextSource.LECHAIM: "Бехукотай",
        TorahTextSource.HEBREW: "בחוקתי",
    },
    34: {
        TorahTextSource.FG: "Бемидбар",
        TorahTextSource.PLAUT: "B’midbar (In the Wilderness)",
        TorahTextSource.LECHAIM: "Бемидбар",
        TorahTextSource.HEBREW: "במדבר",
    },
    35: {
        TorahTextSource.FG: "Носой",
        TorahTextSource.PLAUT: "Naso (Take a Census)",
        TorahTextSource.LECHAIM: "Насо",
        TorahTextSource.HEBREW: "נשא",
    },
    36: {
        TorahTextSource.FG: "Бегаалойсхо",
        TorahTextSource.PLAUT: "B’haalot’cha (When You Raise [the Lamps])",
        TorahTextSource.LECHAIM: "Бегаалотха",
        TorahTextSource.HEBREW: "בהעלותך",
    },
    37: {
        TorahTextSource.FG: "Шлах",
        TorahTextSource.PLAUT: "Sh’lach L’cha (Send [Notables to Scout the Land])",
        TorahTextSource.LECHAIM: "Шлах",
        TorahTextSource.HEBREW: "שלח",
    },
    38: {
        TorahTextSource.FG: "Койрах",
        TorahTextSource.PLAUT: "Korach (Korach)",
        TorahTextSource.LECHAIM: "Корах",
        TorahTextSource.HEBREW: "קרח",
    },
    39: {
        TorahTextSource.FG: "Хукас",
        TorahTextSource.PLAUT: "Chukat (The Ritual Law)",
        TorahTextSource.LECHAIM: "Хукат",
        TorahTextSource.HEBREW: "חקת",
    },
    40: {
        TorahTextSource.FG: "Болок",
        TorahTextSource.PLAUT: "Balak (Balak)",
        TorahTextSource.LECHAIM: "Балак",
        TorahTextSource.HEBREW: "בלק",
    },
    41: {
        TorahTextSource.FG: "Пинхас",
        TorahTextSource.PLAUT: "Pinchas (Phinehas)",
        TorahTextSource.LECHAIM: "Пинхас",
        TorahTextSource.HEBREW: "פנחס",
    },
    42: {
        TorahTextSource.FG: "Матойс",
        TorahTextSource.PLAUT: "Matot (Tribes)",
        TorahTextSource.LECHAIM: "Матот",
        TorahTextSource.HEBREW: "מטות",
    },
    43: {
        TorahTextSource.FG: "Масэй",
        TorahTextSource.PLAUT: "Mas-ei (The Marches)",
        TorahTextSource.LECHAIM: "Масеэй",
        TorahTextSource.HEBREW: "מסעי",
    },
    44: {
        TorahTextSource.FG: "Деворим",
        TorahTextSource.PLAUT: "D’varim (The Words)",
        TorahTextSource.LECHAIM: "Дварим",
        TorahTextSource.HEBREW: "דברים",
    },
    45: {
        TorahTextSource.FG: "Воэсханан",
        TorahTextSource.PLAUT: "Va-et’chanan (I [Moses] Pleaded with the Eternal)",
        TorahTextSource.LECHAIM: "Ваэтханан",
        TorahTextSource.HEBREW: "ואתחנן",
    },
    46: {
        TorahTextSource.FG: "Экев",
        TorahTextSource.PLAUT: "Eikev ([And if You] Obey [These Rules])",
        TorahTextSource.LECHAIM: "Экев",
        TorahTextSource.HEBREW: "עקב",
    },
    47: {
        TorahTextSource.FG: "Рээй",
        TorahTextSource.PLAUT: "R’eih (See [This Day I Set Before You Blessing and Curse])",
        TorahTextSource.LECHAIM: "Реэ",
        TorahTextSource.HEBREW: "ראה",
    },
    48: {
        TorahTextSource.FG: "Шойфтим",
        TorahTextSource.PLAUT: "Shof’tim (Judges)",
        TorahTextSource.LECHAIM: "Шофтим",
        TorahTextSource.HEBREW: "שופטים",
    },
    49: {
        TorahTextSource.FG: "Ки Тейцей",
        TorahTextSource.PLAUT: "Ki’Teitzei (When You Go Out (to Battle))",
        TorahTextSource.LECHAIM: "Ки теце",
        TorahTextSource.HEBREW: "כי תצא",
    },
    50: {
        TorahTextSource.FG: "Ки Совой",
        TorahTextSource.PLAUT: "Ki Tavo (When You Enter [the Land])",
        TorahTextSource.LECHAIM: "Ки таво",
        TorahTextSource.HEBREW: "כי תבוא",
    },
    51: {
        TorahTextSource.FG: "Ницовим",
        TorahTextSource.PLAUT: "Nitzavim (You Stand [This Day])",
        TorahTextSource.LECHAIM: "Ницавим",
        TorahTextSource.HEBREW: "נצבים",
    },
    52: {
        TorahTextSource.FG: "Вайейлех",
        TorahTextSource.PLAUT: "Vayeilech ([Moses] Went)",
        TorahTextSource.LECHAIM: "Вайелех",
        TorahTextSource.HEBREW: "וילך",
    },
    53: {
        TorahTextSource.FG: "Гаазину",
        TorahTextSource.PLAUT: "Haazinu (Listen)",
        TorahTextSource.LECHAIM: "Гаазину",
        TorahTextSource.HEBREW: "האזינו",
    },
    54: {
        TorahTextSource.FG: "Везойс гаБрохо",
        TorahTextSource.PLAUT: "V’zot Hab’rachah (And This is the Blessing)",
        TorahTextSource.LECHAIM: "Везот га-браха",
        TorahTextSource.HEBREW: "וזאת הברכה",
    },
}

parsha_url_names = {
    1: "bereishit",
    2: "noach",
    3: "lech-lecha",
    4: "vayeira",
    5: "chayei-sarah",
    6: "toledot",
    7: "vayeitzei",
    8: "vayishlach",
    9: "vayeishev",
    10: "mikeitz",
    11: "vayigash",
    12: "va-yechi",
    13: "shemot",
    14: "va-eira",
    15: "bo",
    16: "beshalach",
    17: "yitro",
    18: "mishpatim",
    19: "terumah",
    20: "tetzaveh",
    21: "ki-tisa",
    22: "vayakheil",
    23: "pekudei",
    24: "vayikra",
    25: "tzav",
    26: "shemini",
    27: "tazria",
    28: "metzor",
    29: "acharei-mot",
    30: "kedoshim",
    31: "emor",
    32: "behar",
    33: "bechukotai",
    34: "bemidbar",
    35: "naso",
    36: "behaalotecha",
    37: "shelach",
    38: "korach",
    39: "chukat",
    40: "balak",
    41: "pinchas",
    42: "matot",
    43: "mas-ei",
    44: "devarim",
    45: "va-etchanan",
    46: "eikev",
    47: "reeih",
    48: "shofetim",
    49: "ki-teitzei",
    50: "ki-tavo",
    51: "nitzavim",
    52: "vayeilech",
    53: "haazinu",
    54: "vezot-haberachah",
}

TorahTextSource.validate_per_text_source_dict(text_source_marks)
TorahTextSource.validate_per_text_source_dict(text_source_links)
TorahTextSource.validate_per_text_source_dict(text_source_descriptions)
for _, names in torah_book_names.items():
    TorahTextSource.validate_per_text_source_dict(names)
for _, names in parsha_names.items():
    TorahTextSource.validate_per_text_source_dict(names)
TorahTextSource.validate_per_text_source_dict(text_source_languages)


class TorahCommentSource:
    SONCHINO = "sonchino"
    RASHI = "rashi"
    RASHI_ALT = "rashi_alt"
    IBN_EZRA = "ibn-ezra"
    RAMBAN = "ramban"
    OR_HACHAIM = "or_hachaim"

    @classmethod
    def all(cls) -> list[str]:
        return [cls.SONCHINO, cls.RASHI, cls.RASHI_ALT, cls.IBN_EZRA, cls.RAMBAN, cls.OR_HACHAIM]

    @classmethod
    def validate_per_comment_source_dict(cls, d: dict[str, Any]):
        if set(d.keys()) != set(cls.all()):
            raise SystemExit(f"Missing or extra records in per-comment source dict {d}")


comment_source_names = {
    TorahCommentSource.SONCHINO: "Сончино [ФГ]",
    TorahCommentSource.RASHI: "Раши [ФГ]",
    TorahCommentSource.RASHI_ALT: "Раши [Лехаим]",
    TorahCommentSource.IBN_EZRA: "ибн Эзра [Лехаим]",
    TorahCommentSource.RAMBAN: "Рамбан [Chavel]",
    TorahCommentSource.OR_HACHAIM: "Ор ха-Хайим [Munk]",
}


comment_source_links: dict[str, list[str]] = {
    TorahCommentSource.SONCHINO: [
        r"https://toldot.com/Sonchino.html",
        r"https://ru.wikipedia.org/wiki/%D0%93%D0%B5%D1%80%D1%86,_%D0%99%D0%BE%D1%81%D0%B5%D1%84_%D0%A6%D0%B2%D0%B8",
    ],
    TorahCommentSource.RASHI: [
        r"https://toldot.com/TorahRashi.html",
        r"https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D1%88%D0%B8",
    ],
    TorahCommentSource.RASHI_ALT: [],
    TorahCommentSource.IBN_EZRA: [
        r"https://toldot.com/ibnEzra.html",
        r"https://ru.wikipedia.org/wiki/%D0%90%D0%B2%D1%80%D0%B0%D0%B0%D0%BC_%D0%B8%D0%B1%D0%BD_%D0%AD%D0%B7%D1%80%D0%B0",  # noqa
    ],
    TorahCommentSource.RAMBAN: [
        r"https://en.wikipedia.org/wiki/Nachmanides",
        r"https://www.sefaria.org/texts/Tanakh/Rishonim%20on%20Tanakh/Ramban/Torah",
        r"https://www.nli.org.il/he/books/NNL_ALEPH002108945/NLI",
    ],
    TorahCommentSource.OR_HACHAIM: [
        r"https://en.wikipedia.org/wiki/Chaim_ibn_Attar",
        r"https://www.sefaria.org/texts/Tanakh/Acharonim%20on%20Tanakh/Or%20HaChaim/Torah",
        r"https://mysefer.com/Or-HaChaim--Commentary-on-the-Torah-English-5-vol.__p-946.aspx",
        r"https://www.nehora.com/or-hachaim-commentary-on-the-torah/",
    ],
}


comment_source_languages = {
    TorahCommentSource.SONCHINO: IsoLang.RU,
    TorahCommentSource.RASHI: IsoLang.RU,
    TorahCommentSource.RASHI_ALT: IsoLang.RU,
    TorahCommentSource.IBN_EZRA: IsoLang.RU,
    TorahCommentSource.RAMBAN: IsoLang.EN,
    TorahCommentSource.OR_HACHAIM: IsoLang.EN,
}

TorahCommentSource.validate_per_comment_source_dict(comment_source_names)
TorahCommentSource.validate_per_comment_source_dict(comment_source_links)
TorahCommentSource.validate_per_comment_source_dict(comment_source_languages)


TORAH_METADATA = TanakhSectionMetadata(
    title={
        TorahTextSource.FG: "Тора",
        TorahTextSource.LECHAIM: "Тора",
        TorahTextSource.PLAUT: "The Torah",
        TorahTextSource.HEBREW: "תּוֹרָה",
    },
    subtitle=None,
    text_sources=[
        TextSourceInfo(
            key=key,
            mark=text_source_marks[key],
            description=text_source_descriptions[key],
            links=text_source_links[key],
            language=text_source_languages[key],
        )
        for key in TorahTextSource.all()
    ],
    comment_sources=[
        CommentSourceInfo(
            key=key,
            name=comment_source_names[key],
            links=comment_source_links[key],
            language=comment_source_languages[key],
        )
        for key in TorahCommentSource.all()
    ],
    books=[
        TanakhBookInfo(
            id=id,
            name=name,
        )
        for id, name in torah_book_names.items()
    ],
    parshas=[
        ParshaInfo(
            id=parsha_id,
            name=name,
            url_name=parsha_url_names[parsha_id],
            book_id=[
                book_id
                for book_id, (min_parsha_id, max_parsha_id) in torah_book_parsha_ranges.items()
                if min_parsha_id <= parsha_id < max_parsha_id
            ][0],
            chapter_verse_start=chapter_verse_ranges[parsha_id][0],
            chapter_verse_end=chapter_verse_ranges[parsha_id][1],
        )
        for parsha_id, name in parsha_names.items()
    ],
)
