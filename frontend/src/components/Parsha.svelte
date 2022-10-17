<script lang="ts">
    import { getContext } from "svelte";
    import type { Metadata, ParshaData, VerseData, ChapterData } from "../types";
    import VerseDetailsModal from "./VerseDetailsModal.svelte";
    import VerseComments from "./VerseComments.svelte";
    import InlineIcon from "./shared/InlineIcon.svelte";
    import Icon from "./shared/Icon.svelte";
    import Menu from "./Menu.svelte";
    import {
        TextDecorationStyle,
        textDecorationStyleStore,
    } from "../settings/textDecorationStyle";
    import { CommentStyle, commentStyleStore } from "../settings/commentStyle";
    import { textSourcesConfigStore } from "../settings/textSources";

    const metadata: Metadata = getContext("metadata");
    let textDecorationStyle: TextDecorationStyle;
    textDecorationStyleStore.subscribe((v) => {
        textDecorationStyle = v;
    });
    let commentStyle: CommentStyle;
    commentStyleStore.subscribe((v) => {
        commentStyle = v;
    });
    let mainTextSource: string;
    textSourcesConfigStore.subscribe(config => {
        mainTextSource = config.main;
    })

    export let parsha: ParshaData;
    const chapterNumbers = parsha.chapters.map(
        (chapterData) => chapterData.chapter
    );
    chapterNumbers.sort((a, b) => a - b);
    const firstChapterNo = chapterNumbers[0];
    const lastChapterNo = chapterNumbers[chapterNumbers.length - 1];

    const verseId = (chapterNo: number, verseNo: number): number =>
        chapterNo * 100000 + verseNo;

    // @ts-ignore
    const { open } = getContext("simple-modal");

    let inlineVerseDetailsVisible: Map<number, boolean> = new Map();
    for (const chapterData of parsha.chapters) {
        for (const verseData of chapterData.verses) {
            inlineVerseDetailsVisible[
                verseId(chapterData.chapter, verseData.verse)
            ] = false;
        }
    }

    const openVerseDetails = (verse: VerseData, chapter: ChapterData) => {
        if (commentStyle == CommentStyle.MODAL) {
            open(VerseDetailsModal, {
                parsha: parsha,
                verse: verse.verse,
                chapter: chapter.chapter,
            });
        } else if (commentStyle == CommentStyle.INLINE) {
            inlineVerseDetailsVisible[verseId(chapter.chapter, verse.verse)] =
                !inlineVerseDetailsVisible[
                    verseId(chapter.chapter, verse.verse)
                ];
            inlineVerseDetailsVisible = { ...inlineVerseDetailsVisible };
        }
    };
</script>

<Menu homeButton />
<div class="page">
    <div class="container">
        <span class="small-header">
            Книга <b>{metadata.book_names[parsha.book][mainTextSource]}</b>,
            недельный раздел
            <b>{metadata.parsha_names[parsha.parsha][mainTextSource]}</b>, главы
            с <b>{firstChapterNo}</b> по <b>{lastChapterNo}</b>
        </span>
        {#each parsha.chapters as chapter}
            <h2>Глава {chapter.chapter}</h2>
            {#each chapter.verses as verse}
                <span class="verse">
                    <span class="verse-number">{verse.verse}.</span>
                    <span
                        class={textDecorationStyle ===
                        TextDecorationStyle.CLICKABLE_TEXT
                            ? "verse-text clickable"
                            : "verse-text"}
                        on:click={() => {
                            textDecorationStyle ===
                            TextDecorationStyle.CLICKABLE_TEXT
                                ? openVerseDetails(verse, chapter)
                                : null;
                        }}
                        on:keydown={() => {
                            textDecorationStyle ===
                            TextDecorationStyle.CLICKABLE_TEXT
                                ? openVerseDetails(verse, chapter)
                                : null;
                        }}
                    >{verse.text[mainTextSource]}</span>
                    {#if textDecorationStyle === TextDecorationStyle.ASTRERISK}
                        <span
                            class="comment-asterisk"
                            on:click={() => openVerseDetails(verse, chapter)}
                            on:keydown={() => openVerseDetails(verse, chapter)}
                        >
                            <InlineIcon heightEm={0.7}>
                                <Icon icon={"asterisk"} color={"#606060"} />
                            </InlineIcon>
                        </span>
                    {/if}
                </span>
                <div
                    class="inline-verse-comment-container"
                    style={inlineVerseDetailsVisible[
                        verseId(chapter.chapter, verse.verse)
                    ]
                        ? ""
                        : "display: none;"}
                >
                    <VerseComments verseData={verse} />
                </div>
            {/each}
        {/each}
    </div>
</div>

<style>
    div.page {
        display: flex;
        justify-content: center;
        align-items: center;
    }

    div.container {
        text-align: justify;
        width: max(50vw, 600px);
        margin: 4em 10px 4em 10px;
    }

    span.verse {
        /* temp */
        background-color: white;
    }

    span.verse-text {
        margin-right: 0.1em;
    }

    span.comment-asterisk {
        cursor: pointer;
        margin-right: 0.3em;
    }

    span.verse-number {
        color: rgb(105, 105, 105);
        user-select: none;
        margin-right: 0.2em;
    }

    .small-header {
        font-size: medium;
        font-weight: normal;
        margin: 0;
    }

    .inline-verse-comment-container {
        margin-bottom: 0.6em;
        padding: 0 0.6em;
        border-left: 1px black solid;
    }
</style>
