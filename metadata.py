class Translation:
    FG = "fg"


torah_book_names = {
    1: {Translation.FG: "Берейшис"},
    2: {Translation.FG: "Шемот"},
    3: {Translation.FG: "Вайикра"},
    4: {Translation.FG: "Бемидбар"},
    5: {Translation.FG: "Деварим"},
}


torah_book_parsha_ranges: dict[int, tuple[int, int]] = {  # upper bound not included, as in list ranges
    1: (1, 13),
    2: (13, 24),
    3: (24, 34),
    4: (34, 44),
    5: (44, 55),
}


parsha_names = {
    1: {Translation.FG: "Берейшис"},
    2: {Translation.FG: "Нойах"},
    3: {Translation.FG: "Лех Лехо"},
    4: {Translation.FG: "Вайейро"},
    5: {Translation.FG: "Хайей Соро"},
    6: {Translation.FG: "Толдойс"},
    7: {Translation.FG: "Вайейцей"},
    8: {Translation.FG: "Вайишлах"},
    9: {Translation.FG: "Вайейшев"},
    10: {Translation.FG: "Микец"},
    11: {Translation.FG: "Вайигаш"},
    12: {Translation.FG: "Вайхи"},
    13: {Translation.FG: "Шемойс"},
    14: {Translation.FG: "Воэйро"},
    15: {Translation.FG: "Бой"},
    16: {Translation.FG: "Бешалах"},
    17: {Translation.FG: "Йисрой"},
    18: {Translation.FG: "Мишпотим"},
    19: {Translation.FG: "Терумо"},
    20: {Translation.FG: "Тецаве"},
    21: {Translation.FG: "Тисо"},
    22: {Translation.FG: "Вайакгел"},
    23: {Translation.FG: "Пкудей"},
    24: {Translation.FG: "Вайикро"},
    25: {Translation.FG: "Цав"},
    26: {Translation.FG: "Шмини"},
    27: {Translation.FG: "Тазриа"},
    28: {Translation.FG: "Мецойро"},
    29: {Translation.FG: "Ахарей"},
    30: {Translation.FG: "Кдойшим"},
    31: {Translation.FG: "Эмойр"},
    32: {Translation.FG: "Бегар"},
    33: {Translation.FG: "Бехукойсай"},
    34: {Translation.FG: "Бемидбар"},
    35: {Translation.FG: "Носой"},
    36: {Translation.FG: "Бегаалойсхо"},
    37: {Translation.FG: "Шлах"},
    38: {Translation.FG: "Койрах"},
    39: {Translation.FG: "Хукас"},
    40: {Translation.FG: "Болок"},
    41: {Translation.FG: "Пинхас"},
    42: {Translation.FG: "Матойс"},
    43: {Translation.FG: "Масэй"},
    44: {Translation.FG: "Деворим"},
    45: {Translation.FG: "Воэсханан"},
    46: {Translation.FG: "Экев"},
    47: {Translation.FG: "Рээй"},
    48: {Translation.FG: "Шойфтим"},
    49: {Translation.FG: "Ки Тейцей"},
    50: {Translation.FG: "Ки Совой"},
    51: {Translation.FG: "Ницовим"},
    52: {Translation.FG: "Вайейлех"},
    53: {Translation.FG: "Гаазину"},
    54: {Translation.FG: "Везойс гаБрохо"},
}


translation_about_url = {
    Translation.FG: r"http://www.ejwiki.org/wiki/%D0%93%D1%83%D1%80%D1%84%D0%B8%D0%BD%D0%BA%D0%B5%D0%BB%D1%8C,_%D0%A4%D1%80%D0%B8%D0%BC%D0%B0"
}


class Commenter:
    SONCHINO = "sonchino"
    RASHI = "rashi"


commenter_about_url = {
    Commenter.SONCHINO: r"https://ru.wikipedia.org/wiki/%D0%93%D0%B5%D1%80%D1%86,_%D0%99%D0%BE%D1%81%D0%B5%D1%84_%D0%A6%D0%B2%D0%B8",
    Commenter.RASHI: r"https://ru.wikipedia.org/wiki/%D0%A0%D0%B0%D1%88%D0%B8",
}
