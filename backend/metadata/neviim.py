from backend.metadata.types import (
    IsoLang,
    ParshaInfo,
    TanakhBookInfo,
    TanakhSectionMetadata,
    TextSource,
)

MOSAD_RAV_KUK_SOURCE = "mosad-harav-cook"


NEVIIM_METADATA = TanakhSectionMetadata(
    title={MOSAD_RAV_KUK_SOURCE: "Пророки"},
    subtitle=None,
    text_sources=[
        TextSource(
            key=MOSAD_RAV_KUK_SOURCE,
            mark="[МРК]",
            description="Текст в переводе издательства Мосад hаРав Кук, под руководством р. Давида Йосифона",
            links=[
                r"https://toraonline.ru/index.htm",
                r"http://holyscripture.ru/bible/?t=josiphon",
            ],
            language=IsoLang.RU,
        )
    ],
    comment_sources=[],
    books=[
        TanakhBookInfo(
            id=6,
            name={
                MOSAD_RAV_KUK_SOURCE: "Йеhошуа",
            },
        )
    ],
    parshas=[
        ParshaInfo(
            id=55,
            book_id=6,
            chapter_verse_start=(1, 1),
            chapter_verse_end=(11, 40),
            name={
                MOSAD_RAV_KUK_SOURCE: "Йеhошуа 1-11",
            },
        )
    ],
)
