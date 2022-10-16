from typing import Optional


class Translation:
    FG = "fg"
    PLAUT = "plaut"


torah_book_names = {
    1: {Translation.FG: "Берейшис", Translation.PLAUT: "Genesis"},
    2: {Translation.FG: "Шемот", Translation.PLAUT: "Exodus"},
    3: {Translation.FG: "Вайикра", Translation.PLAUT: "Leviticus"},
    4: {Translation.FG: "Бемидбар", Translation.PLAUT: "Numbers"},
    5: {Translation.FG: "Деварим", Translation.PLAUT: "Deuteronomy"},
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
    1: {Translation.FG: "Берейшис", Translation.PLAUT: "B’reishit"},
    2: {Translation.FG: "Нойах", Translation.PLAUT: "Noach"},
    3: {Translation.FG: "Лех Лехо", Translation.PLAUT: "Lech L’cha"},
    4: {Translation.FG: "Вайейро", Translation.PLAUT: "Vayeira"},
    5: {Translation.FG: "Хайей Соро", Translation.PLAUT: "Chayei Sarah"},
    6: {Translation.FG: "Толдойс", Translation.PLAUT: "Tol’dot"},
    7: {Translation.FG: "Вайейцей", Translation.PLAUT: "Vayeitze"},
    8: {Translation.FG: "Вайишлах", Translation.PLAUT: "Vayishlach"},
    9: {Translation.FG: "Вайейшев", Translation.PLAUT: "Vayeishev"},
    10: {Translation.FG: "Микец", Translation.PLAUT: "Mikeitz"},
    11: {Translation.FG: "Вайигаш", Translation.PLAUT: "Vayigash"},
    12: {Translation.FG: "Вайхи", Translation.PLAUT: "Va-y’chi"},
    13: {Translation.FG: "Шемойс", Translation.PLAUT: "Sh’mot"},
    14: {Translation.FG: "Воэйро", Translation.PLAUT: "Va-eira"},
    15: {Translation.FG: "Бой", Translation.PLAUT: "Bo"},
    16: {Translation.FG: "Бешалах", Translation.PLAUT: "B’shalach"},
    17: {Translation.FG: "Йисрой", Translation.PLAUT: "Yitro"},
    18: {Translation.FG: "Мишпотим", Translation.PLAUT: "Mishpatim"},
    19: {Translation.FG: "Терумо", Translation.PLAUT: "T’rumah"},
    20: {Translation.FG: "Тецаве", Translation.PLAUT: "T’tzaveh"},
    21: {Translation.FG: "Тисо", Translation.PLAUT: "Ki Tisa"},
    22: {Translation.FG: "Вайакгел", Translation.PLAUT: "Vayak’heil"},
    23: {Translation.FG: "Пкудей", Translation.PLAUT: "P’kudei"},
    24: {Translation.FG: "Вайикро", Translation.PLAUT: "Vayikra"},
    25: {Translation.FG: "Цав", Translation.PLAUT: "Tzav"},
    26: {Translation.FG: "Шмини", Translation.PLAUT: "Sh’mini"},
    27: {Translation.FG: "Тазриа", Translation.PLAUT: "Tazria"},
    28: {Translation.FG: "Мецойро", Translation.PLAUT: "M’tzor"},
    29: {Translation.FG: "Ахарей", Translation.PLAUT: "Acharei Mot"},
    30: {Translation.FG: "Кдойшим", Translation.PLAUT: "K’doshim"},
    31: {Translation.FG: "Эмойр", Translation.PLAUT: "Emor"},
    32: {Translation.FG: "Бегар", Translation.PLAUT: "B’har"},
    33: {Translation.FG: "Бехукойсай", Translation.PLAUT: "B’chukotai"},
    34: {Translation.FG: "Бемидбар", Translation.PLAUT: "B’midbar"},
    35: {Translation.FG: "Носой", Translation.PLAUT: "Naso"},
    36: {Translation.FG: "Бегаалойсхо", Translation.PLAUT: "B’haalot’cha"},
    37: {Translation.FG: "Шлах", Translation.PLAUT: "Sh’lach L’cha"},
    38: {Translation.FG: "Койрах", Translation.PLAUT: "Korach"},
    39: {Translation.FG: "Хукас", Translation.PLAUT: "Chukat"},
    40: {Translation.FG: "Болок", Translation.PLAUT: "Balak"},
    41: {Translation.FG: "Пинхас", Translation.PLAUT: "Pinchas"},
    42: {Translation.FG: "Матойс", Translation.PLAUT: "Matot"},
    43: {Translation.FG: "Масэй", Translation.PLAUT: "Mas-ei"},
    44: {Translation.FG: "Деворим", Translation.PLAUT: "D’varim"},
    45: {Translation.FG: "Воэсханан", Translation.PLAUT: "Va-et’chanan"},
    46: {Translation.FG: "Экев", Translation.PLAUT: "Eikev"},
    47: {Translation.FG: "Рээй", Translation.PLAUT: "R’eih"},
    48: {Translation.FG: "Шойфтим", Translation.PLAUT: "Shof’tim"},
    49: {Translation.FG: "Ки Тейцей", Translation.PLAUT: "Ki’Teitzei"},
    50: {Translation.FG: "Ки Совой", Translation.PLAUT: "Ki Tavo"},
    51: {Translation.FG: "Ницовим", Translation.PLAUT: "Nitzavim"},
    52: {Translation.FG: "Вайейлех", Translation.PLAUT: "Vayeilech"},
    53: {Translation.FG: "Гаазину", Translation.PLAUT: "Haazinu"},
    54: {Translation.FG: "Везойс гаБрохо", Translation.PLAUT: "V’zot Hab’rachah"},
}


translation_about_url = {
    Translation.FG: r"http://www.ejwiki.org/wiki/%D0%93%D1%83%D1%80%D1%84%D0%B8%D0%BD%D0%BA%D0%B5%D0%BB%D1%8C,_%D0%A4%D1%80%D0%B8%D0%BC%D0%B0",
    Translation.PLAUT: r"https://www.ccarpress.org/content.asp?tid=532",
}


class Commenter:
    SONCHINO = "sonchino"
    RASHI = "rashi"


commenter_about_url = {
    Commenter.SONCHINO: r"https://ru.wikipedia.org/wiki/%D0%93%D0%B5%D1%80%D1%86,_%D0%99%D0%BE%D1%81%D0%B5%D1%84_%D0%A6%D0%B2%D0%B8",
    Commenter.RASHI: r"https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D1%88%D0%B8",
}
