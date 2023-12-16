<script lang="ts">
    import { getContext, onDestroy, setContext } from "svelte";
    import VerseDetailsModal from "./VerseDetailsModal.svelte";
    import VerseComments from "./VerseComments.svelte";
    import Icon from "./shared/Icon.svelte";
    import Menu from "./Menu.svelte";

    import { TextDecorationStyle, textDecorationStyleStore } from "../settings/textDecorationStyle";
    import { CommentStyle, commentStyleStore } from "../settings/commentStyle";
    import { textSourcesConfigStore } from "../settings/textSources";
    import { commentSourcesConfigStore } from "../settings/commentSources";
    import { textDecorationSettingsStore } from "../settings/textDecorationSettings";

    import {
        type SectionMetadata,
        type ParshaData,
        type VerseData,
        type ChapterData,
        type CommentStarToggledEvent,
        type MultisectionMetadata,
        type SectionKey,
        toSingleSection,
    } from "../types";
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
        lookupBookInfo,
        lookupParshaInfo,
    } from "../utils";
    import UpButton from "./shared/UpButton.svelte";
    import VerseBadge from "./VerseBadge.svelte";
    import type { ParshaInfo, TanakhBookInfo } from "../typesGenerated";

    export let parshaData: ParshaData;
    parshaData.chapters.sort((ch1, ch2) => ch1.chapter - ch2.chapter);
    const parshaVerseCoords = getVerseCoords(parshaData);

    const metadata: MultisectionMetadata = getContext("metadata");
    const sectionKey: SectionKey = getContext("sectionKey");
    // NOTE: subtree components may use single-section metadata as before,
    //       just accessing it via a new "sectionMetadata" context
    const sectionMetadata: SectionMetadata = toSingleSection(metadata, sectionKey);
    setContext("sectionMetadata", sectionMetadata);

    let bookNumberInSection: number;
    let bookInfo: TanakhBookInfo;
    let parshaNumberInSection: number;
    let parshaInfo: ParshaInfo;
    $: {
        let bookMatch = lookupBookInfo(sectionMetadata, parshaData.book);
        bookNumberInSection = bookMatch.index;
        bookInfo = bookMatch.bookInfo;

        let parshaMatch = lookupParshaInfo(sectionMetadata, parshaData.parsha);
        parshaNumberInSection = parshaMatch.index;
        parshaInfo = parshaMatch.parshaInfo;
    }

    // non-trivial subscriptions
    let commentStyle: CommentStyle;
    const unsubscribeCommentStyleStore = commentStyleStore.subscribe((v) => {
        commentStyle = v;
        if (commentStyle === CommentStyle.MODAL) {
            try {
                setAllInlineVerseDetailsTo(false);
            } catch (e) {}
        }
    });
    let mainTextSource: string;
    let isMainTextHebrew: boolean;
    const unsubscribeTextSourcesConfigStore = textSourcesConfigStore.subscribe((config) => {
        mainTextSource = config[sectionKey].main;
        isMainTextHebrew = isHebrewTextSource(mainTextSource);
        setPageTitle(sectionMetadata.section.parshas.find((pi) => pi.id === parshaData.parsha).name[mainTextSource]);
    });

    // modal and URL hash stuff setup
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
            onCommentStarToggled: handleCommentStarToggledEvent,
        });

    let urlHashVerseCoords = getUrlHashVerseCoords();
    if (urlHashVerseCoords !== null) {
        if (areInsideVerseCoordsList(urlHashVerseCoords, parshaVerseCoords)) {
            openVerseDetailsModal(urlHashVerseCoords.chapter, urlHashVerseCoords.verse);
        } else {
            setUrlHash("");
        }
    }

    // rendering preparations

    const verseId = (chapterNo: number, verseNo: number): number => chapterNo * 100000 + verseNo;

    //

    let verseIdByCommentId: Record<string, number> = {};
    let starredCommentsCountByVerseId: Record<number, number> = {};

    // filling map to look up verse id by comment id it belongs to
    for (const chapterData of parshaData.chapters) {
        for (const verseData of chapterData.verses) {
            const thisVerseId = verseId(chapterData.chapter, verseData.verse);
            starredCommentsCountByVerseId[thisVerseId] = 0;
            for (const commentDataList of Object.values(verseData.comments)) {
                for (const commentData of commentDataList) {
                    verseIdByCommentId[commentData.id] = thisVerseId;
                    if (commentData.is_starred_by_me === true) {
                        starredCommentsCountByVerseId[thisVerseId]++;
                    }
                }
            }
        }
    }

    function handleCommentStarToggledEvent(event: CustomEvent<CommentStarToggledEvent>) {
        const e = event.detail;
        const increment = e.newIsStarred ? 1 : -1;
        starredCommentsCountByVerseId[verseIdByCommentId[e.commentId]] += increment;
    }

    //

    let inlineVerseDetailsVisibilityMask: Record<number, boolean> = {};

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
            return anyCommentPassesFilters(verseData, $commentSourcesConfigStore[sectionKey]);
        } else return true;
    };

    let currentTextDecorationStyle: TextDecorationStyle;
    textDecorationStyleStore.subscribe((style) => (currentTextDecorationStyle = style));

    const shouldVerseTextBeClickable = (verseData: VerseData) =>
        currentTextDecorationStyle === TextDecorationStyle.CLICKABLE_TEXT && shouldDecorateVerseText(verseData);
    const shouldVerseTextHaveAsterisk = (verseData: VerseData) =>
        currentTextDecorationStyle === TextDecorationStyle.ASTRERISK && shouldDecorateVerseText(verseData);

    onDestroy(() => {
        unsubscribeCommentStyleStore();
        unsubscribeTextSourcesConfigStore();
    });
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
            <p class="header-info"><strong>{sectionMetadata.section.title[mainTextSource]}</strong></p>
            {#if sectionMetadata.section.subtitle}
                <p class="header-info">{sectionMetadata.section.subtitle[mainTextSource]}</p>
            {/if}
            <p class="header-info">
                Книга
                <!-- NOTE: id is meaningless so we need to replace it with index in section maybe? -->
                <!-- <strong>{bookInfo.id}</strong>: -->
                <strong>{bookInfo.name[mainTextSource]}</strong>
            </p>
            <p class="header-info">
                Недельный раздел
                <!-- <strong>{parshaInfo.id}</strong>: -->
                <strong>{parshaInfo.name[mainTextSource]}</strong>
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
                    <span class={isMainTextHebrew ? "verse-number verse-number-hebrew" : "verse-number"}>
                        <span class={isMainTextHebrew ? "verse-number-badge-container-hebrew" : ""}>
                            <VerseBadge
                                starredCommentsCount={starredCommentsCountByVerseId[
                                    verseId(chapter.chapter, verseData.verse)
                                ]}
                            /></span
                        ><span style="width: 0.2em" /><span
                            >{isMainTextHebrew ? `${toHebrewNumberal(verseData.verse)}` : `${verseData.verse}.`}</span
                        >
                    </span>
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
                            <Icon heightEm={0.7} icon={"asterisk"} color={"var(--theme-color-secondary-text)"} />
                        </span>
                    {/if}
                </span>
                {#if shouldDecorateVerseText(verseData) && inlineVerseDetailsVisibilityMask[verseId(chapter.chapter, verseData.verse)]}
                    <div class="inline-verse-comment-container">
                        <VerseComments {verseData} on:commentStarToggled={handleCommentStarToggledEvent} />
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
        color: var(--theme-color-secondary-text);
        user-select: none;
        margin-right: 0.2em;
        display: inline-flex;
        align-items: baseline;
    }

    span.verse-number-hebrew {
        min-width: 2.4em;
        margin-left: 0.1em;
        flex-direction: row-reverse;
    }

    span.verse-number-badge-container-hebrew {
        min-width: 0.8em;
    }

    p.header-info {
        margin: 0.2em 0;
    }

    .inline-verse-comment-container {
        margin: 0.8em 0 0.8em 0.2em;
        padding: 0.2em 0 0.2em 1em;
        border-left: 1px var(--theme-color-secondary-border) solid;
    }

    .no-background-in-unhovered {
        background: transparent;
    }

    button.inline-btn {
        background: var(--theme-color-secondary-background);
        border-color: var(--theme-color-secondary-border);
        cursor: pointer;
        padding: 0.2em 0.6em;
    }
    button.inline-btn:hover {
        filter: brightness(95%);
    }
</style>
