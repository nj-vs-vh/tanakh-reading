from backend.metadata.types import (
    IsoLang,
    ParshaInfo,
    TanakhBookInfo,
    TanakhSectionMetadata,
    TextSource,
)

TEXT_SOURCE = "dummy"


NEVIIM_METADATA = TanakhSectionMetadata(
    title={TEXT_SOURCE: "Пророки"},
    subtitle=None,
    text_sources=[
        TextSource(
            key=TEXT_SOURCE,
            mark="[Dummy]",
            description="Dummy",
            links=[],
            language=IsoLang.RU,
        )
    ],
    comment_sources=[],
    books=[
        TanakhBookInfo(
            id=6,
            name={TEXT_SOURCE: "Йеhошуа"},
        )
    ],
    parshas=[
        ParshaInfo(
            id=100, book_id=6, chapter_verse_start=(1, 1), chapter_verse_end=(2, 2), name={TEXT_SOURCE: "Йеhошуа 1"}
        )
    ],
)
