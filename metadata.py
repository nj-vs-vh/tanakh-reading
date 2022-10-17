from typing import Any


class TextSource:
    FG = "fg"
    PLAUT = "plaut"

    @classmethod
    def all(cls) -> list[str]:
        return [cls.FG, cls.PLAUT]

    @classmethod
    def validate_per_text_source_dict(cls, d: dict[str, Any]):
        if set(d.keys()) != set(cls.all()):
            raise SystemExit(f"Missing or extra records in per-text source dict {d}")


text_source_marks = {TextSource.FG: "[ФГ]", TextSource.PLAUT: "[Plaut]"}


text_source_descriptions = {
    TextSource.FG: "Русский перевод Фримы Гурфинкель",
    TextSource.PLAUT: "Английский перевод «The Torah: A Modern Commentary» под редакцией Гюнтера Плаута",
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
}


torah_book_names = {
    1: {TextSource.FG: "Берейшис", TextSource.PLAUT: "Genesis"},
    2: {TextSource.FG: "Шемот", TextSource.PLAUT: "Exodus"},
    3: {TextSource.FG: "Вайикра", TextSource.PLAUT: "Leviticus"},
    4: {TextSource.FG: "Бемидбар", TextSource.PLAUT: "Numbers"},
    5: {TextSource.FG: "Деварим", TextSource.PLAUT: "Deuteronomy"},
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
    1: {TextSource.FG: "Берейшис", TextSource.PLAUT: "B’reishit"},
    2: {TextSource.FG: "Нойах", TextSource.PLAUT: "Noach"},
    3: {TextSource.FG: "Лех Лехо", TextSource.PLAUT: "Lech L’cha"},
    4: {TextSource.FG: "Вайейро", TextSource.PLAUT: "Vayeira"},
    5: {TextSource.FG: "Хайей Соро", TextSource.PLAUT: "Chayei Sarah"},
    6: {TextSource.FG: "Толдойс", TextSource.PLAUT: "Tol’dot"},
    7: {TextSource.FG: "Вайейцей", TextSource.PLAUT: "Vayeitze"},
    8: {TextSource.FG: "Вайишлах", TextSource.PLAUT: "Vayishlach"},
    9: {TextSource.FG: "Вайейшев", TextSource.PLAUT: "Vayeishev"},
    10: {TextSource.FG: "Микец", TextSource.PLAUT: "Mikeitz"},
    11: {TextSource.FG: "Вайигаш", TextSource.PLAUT: "Vayigash"},
    12: {TextSource.FG: "Вайхи", TextSource.PLAUT: "Va-y’chi"},
    13: {TextSource.FG: "Шемойс", TextSource.PLAUT: "Sh’mot"},
    14: {TextSource.FG: "Воэйро", TextSource.PLAUT: "Va-eira"},
    15: {TextSource.FG: "Бой", TextSource.PLAUT: "Bo"},
    16: {TextSource.FG: "Бешалах", TextSource.PLAUT: "B’shalach"},
    17: {TextSource.FG: "Йисрой", TextSource.PLAUT: "Yitro"},
    18: {TextSource.FG: "Мишпотим", TextSource.PLAUT: "Mishpatim"},
    19: {TextSource.FG: "Терумо", TextSource.PLAUT: "T’rumah"},
    20: {TextSource.FG: "Тецаве", TextSource.PLAUT: "T’tzaveh"},
    21: {TextSource.FG: "Тисо", TextSource.PLAUT: "Ki Tisa"},
    22: {TextSource.FG: "Вайакгел", TextSource.PLAUT: "Vayak’heil"},
    23: {TextSource.FG: "Пкудей", TextSource.PLAUT: "P’kudei"},
    24: {TextSource.FG: "Вайикро", TextSource.PLAUT: "Vayikra"},
    25: {TextSource.FG: "Цав", TextSource.PLAUT: "Tzav"},
    26: {TextSource.FG: "Шмини", TextSource.PLAUT: "Sh’mini"},
    27: {TextSource.FG: "Тазриа", TextSource.PLAUT: "Tazria"},
    28: {TextSource.FG: "Мецойро", TextSource.PLAUT: "M’tzor"},
    29: {TextSource.FG: "Ахарей", TextSource.PLAUT: "Acharei Mot"},
    30: {TextSource.FG: "Кдойшим", TextSource.PLAUT: "K’doshim"},
    31: {TextSource.FG: "Эмойр", TextSource.PLAUT: "Emor"},
    32: {TextSource.FG: "Бегар", TextSource.PLAUT: "B’har"},
    33: {TextSource.FG: "Бехукойсай", TextSource.PLAUT: "B’chukotai"},
    34: {TextSource.FG: "Бемидбар", TextSource.PLAUT: "B’midbar"},
    35: {TextSource.FG: "Носой", TextSource.PLAUT: "Naso"},
    36: {TextSource.FG: "Бегаалойсхо", TextSource.PLAUT: "B’haalot’cha"},
    37: {TextSource.FG: "Шлах", TextSource.PLAUT: "Sh’lach L’cha"},
    38: {TextSource.FG: "Койрах", TextSource.PLAUT: "Korach"},
    39: {TextSource.FG: "Хукас", TextSource.PLAUT: "Chukat"},
    40: {TextSource.FG: "Болок", TextSource.PLAUT: "Balak"},
    41: {TextSource.FG: "Пинхас", TextSource.PLAUT: "Pinchas"},
    42: {TextSource.FG: "Матойс", TextSource.PLAUT: "Matot"},
    43: {TextSource.FG: "Масэй", TextSource.PLAUT: "Mas-ei"},
    44: {TextSource.FG: "Деворим", TextSource.PLAUT: "D’varim"},
    45: {TextSource.FG: "Воэсханан", TextSource.PLAUT: "Va-et’chanan"},
    46: {TextSource.FG: "Экев", TextSource.PLAUT: "Eikev"},
    47: {TextSource.FG: "Рээй", TextSource.PLAUT: "R’eih"},
    48: {TextSource.FG: "Шойфтим", TextSource.PLAUT: "Shof’tim"},
    49: {TextSource.FG: "Ки Тейцей", TextSource.PLAUT: "Ki’Teitzei"},
    50: {TextSource.FG: "Ки Совой", TextSource.PLAUT: "Ki Tavo"},
    51: {TextSource.FG: "Ницовим", TextSource.PLAUT: "Nitzavim"},
    52: {TextSource.FG: "Вайейлех", TextSource.PLAUT: "Vayeilech"},
    53: {TextSource.FG: "Гаазину", TextSource.PLAUT: "Haazinu"},
    54: {TextSource.FG: "Везойс гаБрохо", TextSource.PLAUT: "V’zot Hab’rachah"},
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


commenter_names = {
    Commenter.SONCHINO: "Сончино",
    Commenter.RASHI: "Раши",
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
}
