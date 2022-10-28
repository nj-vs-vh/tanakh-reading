<script lang="ts">
    import { getContext } from "svelte";
    import VerseDetailsModal from "./VerseDetailsModal.svelte";
    import VerseComments from "./VerseComments.svelte";
    import Icon from "./shared/Icon.svelte";
    import Menu from "./Menu.svelte";

    import { TextDecorationStyle, textDecorationStyleStore } from "../settings/textDecorationStyle";
    import { CommentStyle, commentStyleStore } from "../settings/commentStyle";
    import { textSourcesConfigStore } from "../settings/textSources";
    import { CommentFilters, commentFiltersStore } from "../settings/commentFilters";
    import { TextDecorationSettings, textDecorationSettingsStore } from "../settings/textDecorationSettings";

    import type { Metadata, ParshaData, VerseData, ChapterData } from "../types";
    import {
        anyCommentPassesFilters,
        areInsideVerseCoordsList,
        getUrlHashVerseCoords,
        getVerseCoords,
        setUrlHash,
        verseCoords2string,
    } from "../utils";

    // context and settings subscription
    const metadata: Metadata = getContext("metadata");

    let textDecorationSettings: TextDecorationSettings;
    textDecorationSettingsStore.subscribe((v) => {
        textDecorationSettings = v;
    });
    let textDecorationStyle: TextDecorationStyle;
    textDecorationStyleStore.subscribe((v) => {
        textDecorationStyle = v;
    });
    let commentStyle: CommentStyle;
    commentStyleStore.subscribe((v) => {
        commentStyle = v;
    });
    let mainTextSource: string;
    textSourcesConfigStore.subscribe((config) => {
        mainTextSource = config.main;
    });
    let commentFilters: CommentFilters;
    commentFiltersStore.subscribe((v) => {
        commentFilters = v;
    });

    export let parshaData: ParshaData;
    parshaData.chapters.sort((ch1, ch2) => ch1.chapter - ch2.chapter);
    const parshaVerseCoords = getVerseCoords(parshaData);
    const firstParshaVerseCoords = parshaVerseCoords[0];
    const lastParshaVerseCoords = parshaVerseCoords[parshaVerseCoords.length - 1];

    const verseId = (chapterNo: number, verseNo: number): number => chapterNo * 100000 + verseNo;

    // @ts-ignore
    const { open } = getContext("simple-modal");
    const openVerseDetailsModal = (chapter: number, verse: number) =>
        open(VerseDetailsModal, {
            parsha: parshaData,
            chapter: chapter,
            verse: verse,
        });

    let urlHashVerseCoords = getUrlHashVerseCoords();
    if (urlHashVerseCoords !== null) {
        if (areInsideVerseCoordsList(urlHashVerseCoords, parshaVerseCoords)) {
            openVerseDetailsModal(urlHashVerseCoords.chapter, urlHashVerseCoords.verse);
        } else {
            setUrlHash("");
        }
    }

    let inlineVerseDetailsVisible: Map<number, boolean> = new Map();
    for (const chapterData of parshaData.chapters) {
        for (const verseData of chapterData.verses) {
            inlineVerseDetailsVisible[verseId(chapterData.chapter, verseData.verse)] = false;
        }
    }

    const openVerseDetails = (verse: VerseData, chapter: ChapterData) => {
        if (commentStyle == CommentStyle.MODAL) {
            openVerseDetailsModal(chapter.chapter, verse.verse);
        } else if (commentStyle == CommentStyle.INLINE) {
            inlineVerseDetailsVisible[verseId(chapter.chapter, verse.verse)] =
                !inlineVerseDetailsVisible[verseId(chapter.chapter, verse.verse)];
            inlineVerseDetailsVisible = { ...inlineVerseDetailsVisible };
        }
    };

    let isDecorated: (verseData: VerseData) => boolean;
    let isClickableText: (verseData: VerseData) => boolean;
    let isAstreisk: (verseData: VerseData) => boolean;

    $: {
        isDecorated = (verseData: VerseData): boolean => {
            if (textDecorationSettings.onlyDecorateTextWithComments) {
                return anyCommentPassesFilters(verseData, commentFilters);
            } else return true;
        };
        isClickableText = (v) => textDecorationStyle === TextDecorationStyle.CLICKABLE_TEXT && isDecorated(v);
        isAstreisk = (v) => textDecorationStyle === TextDecorationStyle.ASTRERISK && isDecorated(v);
    }
</script>

<Menu
    on:verseSearchResult={(event) => {
        if (event.detail.parsha === parshaData.parsha) {
            openVerseDetailsModal(event.detail.chapter, event.detail.verse);
        }
    }}
    homeButton
/>
<div class="page">
    <div class="container">
        <span class="small-header">
            Книга
            <b
                >{parshaData.book}
                {metadata.book_names[parshaData.book][mainTextSource]}</b
            >, недельный раздел
            <b
                >{parshaData.parsha}
                {metadata.parsha_names[parshaData.parsha][mainTextSource]}</b
            >,
            <span style="white-space: nowrap;">
                стихи
                <b>{verseCoords2string(firstParshaVerseCoords)}</b>
                &ndash;
                <b>{verseCoords2string(lastParshaVerseCoords)}</b>
            </span>
        </span>
        {#each parshaData.chapters as chapter}
            <h2>Глава {chapter.chapter}</h2>
            {#each chapter.verses as verseData}
                <span class="verse">
                    <span class="verse-number">{verseData.verse}.</span>
                    <span
                        class={isClickableText(verseData)
                            ? textDecorationSettings.onlyDecorateTextWithComments
                                ? "verse-text clickable"
                                : "verse-text clickable no-background-in-unhovered"
                            : "verse-text"}
                        on:click={() => {
                            isClickableText(verseData) ? openVerseDetails(verseData, chapter) : null;
                        }}
                        on:keydown={() => {
                            isClickableText(verseData) ? openVerseDetails(verseData, chapter) : null;
                        }}>{verseData.text[mainTextSource]}</span
                    >
                    {#if isAstreisk(verseData)}
                        <span
                            class="comment-asterisk"
                            on:click={() => openVerseDetails(verseData, chapter)}
                            on:keydown={() => openVerseDetails(verseData, chapter)}
                        >
                            <Icon heightEm={0.7} icon={"asterisk"} color={"#606060"} />
                        </span>
                    {/if}
                </span>
                <div
                    class="inline-verse-comment-container"
                    style={inlineVerseDetailsVisible[verseId(chapter.chapter, verseData.verse)] ? "" : "display: none;"}
                >
                    <VerseComments {verseData} parsha={parshaData.parsha} chapter={chapter.chapter} />
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
        margin: 0.6em 0;
        padding: 0 0.6em;
    }

    .no-background-in-unhovered {
        background: transparent;
    }
</style>
