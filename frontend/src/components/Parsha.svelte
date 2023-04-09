<script lang="ts">
    import { getContext } from "svelte";
    import VerseDetailsModal from "./VerseDetailsModal.svelte";
    import VerseComments from "./VerseComments.svelte";
    import Icon from "./shared/Icon.svelte";
    import Menu from "./Menu.svelte";

    import { TextDecorationStyle, textDecorationStyleStore } from "../settings/textDecorationStyle";
    import { CommentStyle, commentStyleStore } from "../settings/commentStyle";
    import { textSourcesConfigStore } from "../settings/textSources";
    import { commentSourcesConfigStore } from "../settings/commentSources";
    import { textDecorationSettingsStore } from "../settings/textDecorationSettings";

    import type { Metadata, ParshaData, VerseData, ChapterData } from "../types";
    import {
        anyCommentPassesFilters,
        areInsideVerseCoordsList,
        getUrlHashVerseCoords,
        getVerseCoords,
        toHebrewNumberal,
        isHebrewTextSource,
        setUrlHash,
        verseCoords2String,
        setPageTitle,
    } from "../utils";
    import UpButton from "./shared/UpButton.svelte";

    export let parshaData: ParshaData;
    parshaData.chapters.sort((ch1, ch2) => ch1.chapter - ch2.chapter);

    // context and settings subscription
    const metadata: Metadata = getContext("metadata");

    let commentStyle: CommentStyle;
    commentStyleStore.subscribe((v) => {
        commentStyle = v;
        if (commentStyle === CommentStyle.MODAL) {
            try {
                setAllInlineVerseDetailsTo(false);
            } catch (e) {}
        }
    });
    let mainTextSource: string;
    let isMainTextHebrew: boolean;
    textSourcesConfigStore.subscribe((config) => {
        mainTextSource = config.main;
        isMainTextHebrew = isHebrewTextSource(mainTextSource);
        setPageTitle(metadata.parsha_names[parshaData.parsha][mainTextSource]);
    });

    const parshaVerseCoords = getVerseCoords(parshaData);
    const verseId = (chapterNo: number, verseNo: number): number => chapterNo * 100000 + verseNo;

    // @ts-ignore
    const { open, close } = getContext("simple-modal");

    window.addEventListener("popstate", () => {
        // close window on "back" in history
        try {
            close();
        } catch (e) {}
    });

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

    let inlineVerseDetailsVisibilityMask: Map<number, boolean> = new Map();

    function setAllInlineVerseDetailsTo(value: boolean) {
        for (const chapterData of parshaData.chapters) {
            for (const verseData of chapterData.verses) {
                inlineVerseDetailsVisibilityMask[verseId(chapterData.chapter, verseData.verse)] = value;
            }
        }
    }

    setAllInlineVerseDetailsTo(false);

    const openVerseDetails = (verse: VerseData, chapter: ChapterData) => {
        if (commentStyle == CommentStyle.MODAL) {
            openVerseDetailsModal(chapter.chapter, verse.verse);
        } else if (commentStyle == CommentStyle.INLINE) {
            inlineVerseDetailsVisibilityMask[verseId(chapter.chapter, verse.verse)] =
                !inlineVerseDetailsVisibilityMask[verseId(chapter.chapter, verse.verse)];
        }
    };

    const shouldDecorateVerseText = (verseData: VerseData): boolean => {
        if ($textDecorationSettingsStore.onlyDecorateTextWithComments) {
            return anyCommentPassesFilters(verseData, $commentSourcesConfigStore);
        } else return true;
    };

    const shouldVerseTextBeClickable = (v: VerseData) =>
        $textDecorationStyleStore === TextDecorationStyle.CLICKABLE_TEXT && shouldDecorateVerseText(v);
    const shouldVerseTextHaveAsterisk = (v: VerseData) =>
        $textDecorationStyleStore === TextDecorationStyle.ASTRERISK && shouldDecorateVerseText(v);
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
        <div>
            <p class="header-info">
                Книга
                <strong>{parshaData.book}</strong>:
                <strong>{metadata.book_names[parshaData.book][mainTextSource]}</strong>
            </p>
            <p class="header-info">
                Недельный раздел
                <strong>{parshaData.parsha}</strong>:
                <strong>{metadata.parsha_names[parshaData.parsha][mainTextSource]}</strong>
            </p>
            <p class="header-info">
                <span style="white-space: nowrap;">
                    Стихи
                    <strong>{verseCoords2String(parshaVerseCoords[0])}</strong>
                    &ndash;
                    <strong>{verseCoords2String(parshaVerseCoords[parshaVerseCoords.length - 1])}</strong>
                </span>
            </p>
        </div>
        {#if commentStyle === CommentStyle.INLINE}
            <div style="margin-top: 1em;">
                <button class="inline-btn" on:click={() => setAllInlineVerseDetailsTo(true)}>Развернуть</button>
                или
                <button class="inline-btn" on:click={() => setAllInlineVerseDetailsTo(false)}>свернуть</button>
                все комментарии
            </div>
        {/if}
        {#each parshaData.chapters as chapter}
            <h2>Глава {chapter.chapter}</h2>
            {#each chapter.verses as verseData}
                <span class={isMainTextHebrew ? "verse verse-hebrew" : "verse"}>
                    <span class={isMainTextHebrew ? "verse-number verse-number-hebrew" : "verse-number"}
                        >{isMainTextHebrew ? `${toHebrewNumberal(verseData.verse)}` : `${verseData.verse}.`}</span
                    >
                    <span
                        class={shouldVerseTextBeClickable(verseData)
                            ? $textDecorationSettingsStore.onlyDecorateTextWithComments
                                ? "verse-text clickable"
                                : "verse-text clickable no-background-in-unhovered"
                            : "verse-text"}
                        style={isMainTextHebrew ? "font-size: x-large;" : ""}
                        on:click={() => {
                            shouldVerseTextBeClickable(verseData) ? openVerseDetails(verseData, chapter) : null;
                        }}
                        on:keydown={() => {
                            shouldVerseTextBeClickable(verseData) ? openVerseDetails(verseData, chapter) : null;
                        }}>{verseData.text[mainTextSource]}</span
                    >
                    {#if shouldVerseTextHaveAsterisk(verseData)}
                        <span
                            class="comment-asterisk"
                            on:click={() => openVerseDetails(verseData, chapter)}
                            on:keydown={() => openVerseDetails(verseData, chapter)}
                        >
                            <Icon heightEm={0.7} icon={"asterisk"} color={"#aaaaaa"} />
                        </span>
                    {/if}
                </span>
                {#if shouldDecorateVerseText(verseData) && inlineVerseDetailsVisibilityMask[verseId(chapter.chapter, verseData.verse)]}
                    <div class="inline-verse-comment-container">
                        <VerseComments {verseData} />
                        <UpButton
                            on:up={() => {
                                inlineVerseDetailsVisibilityMask[verseId(chapter.chapter, verseData.verse)] = false;
                            }}
                        />
                    </div>
                {/if}
            {/each}
        {/each}
    </div>
</div>

<style>
    div.page {
        display: flex;
        justify-content: center;
    }

    div.container {
        text-align: justify;
        width: max(50vw, 600px);
        margin: 4em 10px 4em 10px;
    }

    span.verse {
        /* dummy */
        background-color: transparent;
    }

    span.verse-hebrew {
        width: 100%;
        text-align: right;
        display: flex;
        flex-direction: row-reverse;
        align-items: baseline;
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

    span.verse-number-hebrew {
        min-width: 1.6em;
        margin-left: 0.1em;
    }

    p.header-info {
        margin: 0.2em 0;
    }

    .inline-verse-comment-container {
        margin: 0.8em 0 0.8em 0.2em;
        padding: 0.2em 0 0.2em 1em;
        border-left: 1px rgb(189, 189, 189) solid;
    }

    .no-background-in-unhovered {
        background: transparent;
    }

    button.inline-btn {
        background: rgb(240, 240, 240);
        border-color: grey;
        cursor: pointer;
        padding: 0.2em 0.6em;
    }
    button.inline-btn:hover {
        border-color: black;
    }
    button.inline-btn:active {
        background: rgb(231, 231, 231);
    }
</style>
