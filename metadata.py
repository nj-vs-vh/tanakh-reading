from typing import Any


class TextSource:
    FG = "fg"
    PLAUT = "plaut"
    LECHAIM = "lechaim"

    @classmethod
    def all(cls) -> list[str]:
        return [cls.FG, cls.PLAUT, cls.LECHAIM]

    @classmethod
    def validate_per_text_source_dict(cls, d: dict[str, Any]):
        if set(d.keys()) != set(cls.all()):
            raise SystemExit(f"Missing or extra records in per-text source dict {d}")


text_source_marks = {TextSource.FG: "[ФГ]", TextSource.PLAUT: "[Plaut]", TextSource.LECHAIM: "[Лехаим]"}


text_source_descriptions = {
    TextSource.FG: "Русский перевод Фримы Гурфинкель",
    TextSource.PLAUT: "Английский перевод «The Torah: A Modern Commentary» под редакцией Гюнтера Плаута",
    TextSource.LECHAIM: "Русский перевод журнала «Лехаим», авторы не указаны",
}


text_source_links = {
    TextSource.FG: [
        r"http://www.shabat-shalom.info/books/Tanach-ru/Chumash_Rashi/index.htm",
        r"http://www.ejwiki.org/wiki/%D0%93%D1%83%D1%80%D1%84%D0%B8%D0%BD%D0%BA%D0%B5%D0%BB%D1%8C,_%D0%A4%D1%80%D0%B8%D0%BC%D0%B0",
        r"https://esxatos.com/gurfinel-tora-tanah-28-knig-1-fayl",
    ],
    TextSource.PLAUT: [
        r"https://reformjudaism.org/learning/torah-study/english-translations-torah-portions",
        r"https://www.ccarpress.org/shopping_product_detail.asp?pid=50297",
        r"https://www.ccarpress.org/content.asp?tid=532",
    ],
    TextSource.LECHAIM: [
        r"https://lechaim.ru/torah/",
    ],
}


torah_book_names = {
    1: {
        TextSource.FG: "Берейшис",
        TextSource.PLAUT: "Genesis",
        TextSource.LECHAIM: "Берешит",
    },
    2: {
        TextSource.FG: "Шемот",
        TextSource.PLAUT: "Exodus",
        TextSource.LECHAIM: "Шмот",
    },
    3: {
        TextSource.FG: "Вайикра",
        TextSource.PLAUT: "Leviticus",
        TextSource.LECHAIM: "Ваикра",
    },
    4: {
        TextSource.FG: "Бемидбар",
        TextSource.PLAUT: "Numbers",
        TextSource.LECHAIM: "Бемидбар",
    },
    5: {
        TextSource.FG: "Деварим",
        TextSource.PLAUT: "Deuteronomy",
        TextSource.LECHAIM: "Дварим",
    },
}


torah_book_parsha_ranges: dict[int, tuple[int, int]] = {  # upper bound not included, as in list ranges
    1: (1, 13),
    2: (13, 24),
    3: (24, 34),
    4: (34, 44),
    5: (44, 55),
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
    },
    2: {
        TextSource.FG: "Нойах",
        TextSource.PLAUT: "Noach (Noah)",
        TextSource.LECHAIM: "Ноах",
    },
    3: {
        TextSource.FG: "Лех Лехо",
        TextSource.PLAUT: "Lech L’cha (Go Forth)",
        TextSource.LECHAIM: "Лех-леха",
    },
    4: {
        TextSource.FG: "Вайейро",
        TextSource.PLAUT: "Vayeira (I (God) Appeared [to Abraham, Isaac, and Jacob])",
        TextSource.LECHAIM: "Вайера",
    },
    5: {
        TextSource.FG: "Хайей Соро",
        TextSource.PLAUT: "Chayei Sarah (The Life of Sarah)",
        TextSource.LECHAIM: "Хайей сара",
    },
    6: {
        TextSource.FG: "Толдойс",
        TextSource.PLAUT: "Tol’dot (The Generations [of Isaac])",
        TextSource.LECHAIM: "Тольдот",
    },
    7: {
        TextSource.FG: "Вайейцей",
        TextSource.PLAUT: "Vayeitze (And [Jacob] Left)",
        TextSource.LECHAIM: "Вайеце",
    },
    8: {
        TextSource.FG: "Вайишлах",
        TextSource.PLAUT: "Vayishlach ([Jacob] Sent)",
        TextSource.LECHAIM: "Ваишлах",
    },
    9: {
        TextSource.FG: "Вайейшев",
        TextSource.PLAUT: "Vayeishev ([Jacob] Settled)",
        TextSource.LECHAIM: "Вайешев",
    },
    10: {
        TextSource.FG: "Микец",
        TextSource.PLAUT: "Mikeitz (After [Two Years])",
        TextSource.LECHAIM: "Микец",
    },
    11: {
        TextSource.FG: "Вайигаш",
        TextSource.PLAUT: "Vayigash (And [Judah] Approached [Joseph])",
        TextSource.LECHAIM: "Ваигаш",
    },
    12: {
        TextSource.FG: "Вайхи",
        TextSource.PLAUT: "Va-y’chi ([Jacob] Lived)",
        TextSource.LECHAIM: "Вайехи",
    },
    13: {
        TextSource.FG: "Шемойс",
        TextSource.PLAUT: "Sh’mot (Names)",
        TextSource.LECHAIM: "Шмот",
    },
    14: {
        TextSource.FG: "Воэйро",
        TextSource.PLAUT: "Va-eira (I (God) Appeared [to Abraham, Isaac, and Jacob])",
        TextSource.LECHAIM: "Ваэра",
    },
    15: {
        TextSource.FG: "Бой",
        TextSource.PLAUT: "Bo (Go [to Pharaoh])",
        TextSource.LECHAIM: "Бо",
    },
    16: {
        TextSource.FG: "Бешалах",
        TextSource.PLAUT: "B’shalach (Now When [Pharaoh] Let [the People] Go)",
        TextSource.LECHAIM: "Бешалах",
    },
    17: {
        TextSource.FG: "Йисрой",
        TextSource.PLAUT: "Yitro (Jethro)",
        TextSource.LECHAIM: "Итро",
    },
    18: {
        TextSource.FG: "Мишпотим",
        TextSource.PLAUT: "Mishpatim ([These Are the] Rules)",
        TextSource.LECHAIM: "Мишпатим",
    },
    19: {
        TextSource.FG: "Терумо",
        TextSource.PLAUT: "T’rumah (Gifts)",
        TextSource.LECHAIM: "Трума",
    },
    20: {
        TextSource.FG: "Тецаве",
        TextSource.PLAUT: "T’tzaveh ([You] Shall Further Instruct)",
        TextSource.LECHAIM: "Тецаве",
    },
    21: {
        TextSource.FG: "Тисо",
        TextSource.PLAUT: "Ki Tisa (When You Take a Census)",
        TextSource.LECHAIM: "Ки тиса",
    },
    22: {
        TextSource.FG: "Вайакгел",
        TextSource.PLAUT: "Vayak’heil ([Moses] Assembled)",
        TextSource.LECHAIM: "Ваякгель",
    },
    23: {
        TextSource.FG: "Пкудей",
        TextSource.PLAUT: "P’kudei ([The] Records [of the Tabernacle])",
        TextSource.LECHAIM: "Пекудей",
    },
    24: {
        TextSource.FG: "Вайикро",
        TextSource.PLAUT: "Vayikra ([God] Called Out)",
        TextSource.LECHAIM: "Ваикра",
    },
    25: {
        TextSource.FG: "Цав",
        TextSource.PLAUT: "Tzav (Command [Aaron and His Sons])",
        TextSource.LECHAIM: "Цав",
    },
    26: {
        TextSource.FG: "Шмини",
        TextSource.PLAUT: "Sh’mini (The Eighth [Day])",
        TextSource.LECHAIM: "Шмини",
    },
    27: {
        TextSource.FG: "Тазриа",
        TextSource.PLAUT: "Tazria (Bearing Seed)",
        TextSource.LECHAIM: "Тазриа",
    },
    28: {
        TextSource.FG: "Мецойро",
        TextSource.PLAUT: "M’tzor (A Leper)",
        TextSource.LECHAIM: "Мецора",
    },
    29: {
        TextSource.FG: "Ахарей",
        TextSource.PLAUT: "Acharei Mot (After the Death [of the Two Sons of Aaron])",
        TextSource.LECHAIM: "Ахарей мот",
    },
    30: {
        TextSource.FG: "Кдойшим",
        TextSource.PLAUT: "K’doshim ([You Shall Be] Holy)",
        TextSource.LECHAIM: "Кдошим",
    },
    31: {
        TextSource.FG: "Эмойр",
        TextSource.PLAUT: "Emor (Speak)",
        TextSource.LECHAIM: "Эмор",
    },
    32: {
        TextSource.FG: "Бегар",
        TextSource.PLAUT: "B’har (On Mount [Sinai])",
        TextSource.LECHAIM: "Бегар",
    },
    33: {
        TextSource.FG: "Бехукойсай",
        TextSource.PLAUT: "B’chukotai (My Laws)",
        TextSource.LECHAIM: "Бехукотай",
    },
    34: {
        TextSource.FG: "Бемидбар",
        TextSource.PLAUT: "B’midbar (In the Wilderness)",
        TextSource.LECHAIM: "Бемидбар",
    },
    35: {
        TextSource.FG: "Носой",
        TextSource.PLAUT: "Naso (Take a Census)",
        TextSource.LECHAIM: "Насо",
    },
    36: {
        TextSource.FG: "Бегаалойсхо",
        TextSource.PLAUT: "B’haalot’cha (When You Raise [the Lamps])",
        TextSource.LECHAIM: "Бегаалотха",
    },
    37: {
        TextSource.FG: "Шлах",
        TextSource.PLAUT: "Sh’lach L’cha (Send [Notables to Scout the Land])",
        TextSource.LECHAIM: "Шлах",
    },
    38: {
        TextSource.FG: "Койрах",
        TextSource.PLAUT: "Korach (Korach)",
        TextSource.LECHAIM: "Корах",
    },
    39: {
        TextSource.FG: "Хукас",
        TextSource.PLAUT: "Chukat (The Ritual Law)",
        TextSource.LECHAIM: "Хукат",
    },
    40: {
        TextSource.FG: "Болок",
        TextSource.PLAUT: "Balak (Balak)",
        TextSource.LECHAIM: "Балак",
    },
    41: {
        TextSource.FG: "Пинхас",
        TextSource.PLAUT: "Pinchas (Phinehas)",
        TextSource.LECHAIM: "Пинхас",
    },
    42: {
        TextSource.FG: "Матойс",
        TextSource.PLAUT: "Matot (Tribes)",
        TextSource.LECHAIM: "Матот",
    },
    43: {
        TextSource.FG: "Масэй",
        TextSource.PLAUT: "Mas-ei (The Marches)",
        TextSource.LECHAIM: "Масеэй",
    },
    44: {
        TextSource.FG: "Деворим",
        TextSource.PLAUT: "D’varim (The Words)",
        TextSource.LECHAIM: "Дварим",
    },
    45: {
        TextSource.FG: "Воэсханан",
        TextSource.PLAUT: "Va-et’chanan (I [Moses] Pleaded with the Eternal)",
        TextSource.LECHAIM: "Ваэтханан",
    },
    46: {
        TextSource.FG: "Экев",
        TextSource.PLAUT: "Eikev ([And if You] Obey [These Rules])",
        TextSource.LECHAIM: "Экев",
    },
    47: {
        TextSource.FG: "Рээй",
        TextSource.PLAUT: "R’eih (See [This Day I Set Before You Blessing and Curse])",
        TextSource.LECHAIM: "Реэ",
    },
    48: {
        TextSource.FG: "Шойфтим",
        TextSource.PLAUT: "Shof’tim (Judges)",
        TextSource.LECHAIM: "Шофтим",
    },
    49: {
        TextSource.FG: "Ки Тейцей",
        TextSource.PLAUT: "Ki’Teitzei (When You Go Out (to Battle))",
        TextSource.LECHAIM: "Ки теце",
    },
    50: {
        TextSource.FG: "Ки Совой",
        TextSource.PLAUT: "Ki Tavo (When You Enter [the Land])",
        TextSource.LECHAIM: "Ки таво",
    },
    51: {
        TextSource.FG: "Ницовим",
        TextSource.PLAUT: "Nitzavim (You Stand [This Day])",
        TextSource.LECHAIM: "Ницавим",
    },
    52: {
        TextSource.FG: "Вайейлех",
        TextSource.PLAUT: "Vayeilech ([Moses] Went)",
        TextSource.LECHAIM: "Вайелех",
    },
    53: {
        TextSource.FG: "Гаазину",
        TextSource.PLAUT: "Haazinu (Listen)",
        TextSource.LECHAIM: "Гаазину",
    },
    54: {
        TextSource.FG: "Везойс гаБрохо",
        TextSource.PLAUT: "V’zot Hab’rachah (And This is the Blessing)",
        TextSource.LECHAIM: "Везот га-браха",
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


commenter_names = {
    Commenter.SONCHINO: "Сончино [ФГ]",
    Commenter.RASHI: "Раши [ФГ]",
    Commenter.RASHI_ALT: "Раши [Лехаим]",
    Commenter.IBN_EZRA: "ибн Эзра [Лехаим]",
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
        r"https://ru.wikipedia.org/wiki/%D0%90%D0%B2%D1%80%D0%B0%D0%B0%D0%BC_%D0%B8%D0%B1%D0%BD_%D0%AD%D0%B7%D1%80%D0%B0",
    ],
}
