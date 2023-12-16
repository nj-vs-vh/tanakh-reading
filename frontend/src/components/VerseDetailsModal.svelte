<script lang="ts">
    import { getContext, onDestroy, setContext } from "svelte";
    import Keydown from "svelte-keydown";
    import { swipe } from "svelte-gestures";
    import {
        type CommentStarToggledEvent,
        type SectionMetadata,
        type ParshaData,
        type VerseData,
        type MultisectionMetadata,
        toSingleSection,
    } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";
    import VerseComments from "./VerseComments.svelte";
    import Icon from "./shared/Icon.svelte";
    import {
        areInsideVerseCoordsList,
        getVerseCoords,
        VerseCoords,
        versePath,
        verseCoords2String,
        bookNoByParsha,
        lookupBookInfo,
        findBookSectionKey,
    } from "../utils";
    import { isEditingStore } from "../editing";
    import VerseTextBadge from "./VerseTextBadge.svelte";

    export let parsha: ParshaData;
    export let verse: number;
    export let chapter: number;
    export let navigable: boolean = true;

    const metadata: MultisectionMetadata = getContext("metadata");

    // NOTE: since modal is in a separate subtree, it doesn't get section key
    // and section metadata contexts...
    // so, we rebuild them here
    const sk = findBookSectionKey(metadata, parsha.book);
    const sectionMetadata: SectionMetadata = toSingleSection(metadata, sk);
    setContext("sectionKey", sk);
    setContext("sectionMetadata", sectionMetadata);

    let textSources: Array<string>;
    const textSourcesConfigStoreUnsubscribe = textSourcesConfigStore.subscribe((config) => {
        textSources = [];
        textSources.push(config[sk].main);
        for (const [source, isEnabled] of Object.entries(config[sk].enabledInDetails)) {
            if (isEnabled && source != config[sk].main) textSources.push(source);
        }
    });

    const parshaVerseCoords = getVerseCoords(parsha);

    export let onCommentStarToggled: (e: CustomEvent<CommentStarToggledEvent>) => void = (e) => {};

    let isCurrentVerseLinkCopied = false;

    let currentVerseCoords: VerseCoords = { chapter: chapter, verse: verse };

    // @ts-ignore
    const { close } = getContext("simple-modal");
    if (!areInsideVerseCoordsList(currentVerseCoords, parshaVerseCoords)) {
        close();
    }

    function findVerseCoords(chapterNo: number, verseNo: number): VerseCoords | null {
        const chapterData = parsha.chapters.find((ch) => ch.chapter === chapterNo);
        if (chapterData === undefined) return null;
        let verseData: VerseData | null = null;
        if (verseNo >= 0) verseData = chapterData.verses.find((vd) => vd.verse === verseNo);
        // support for Python-like negative verse index
        else
            verseData = chapterData.verses.find(
                (vd) =>
                    vd.verse ===
                    Math.max.apply(
                        Math,
                        chapterData.verses.map((v) => v.verse),
                    ) +
                        verseNo +
                        1,
            );
        if (verseData === undefined) return null;
        else return { chapter: chapterData.chapter, verse: verseData.verse };
    }

    let prevVerseCoords: VerseCoords | null;
    let nextVerseCoords: VerseCoords | null;
    let currentVerseData: VerseData;

    $: {
        currentVerseData = parsha.chapters
            .find((ch) => ch.chapter === currentVerseCoords.chapter)
            .verses.find((v) => v.verse === currentVerseCoords.verse);

        prevVerseCoords = findVerseCoords(currentVerseCoords.chapter, currentVerseCoords.verse - 1);
        if (prevVerseCoords === null) prevVerseCoords = findVerseCoords(currentVerseCoords.chapter - 1, -1);
        nextVerseCoords = findVerseCoords(currentVerseCoords.chapter, currentVerseCoords.verse + 1);
        if (nextVerseCoords === null) nextVerseCoords = findVerseCoords(currentVerseCoords.chapter + 1, 1);
    }

    let containerEl: HTMLElement;

    function prevVerse() {
        if (!$isEditingStore && prevVerseCoords !== null) {
            currentVerseCoords = prevVerseCoords;
            isCurrentVerseLinkCopied = false;
            containerEl.scrollIntoView();
        }
    }

    function nextVerse() {
        if (!$isEditingStore && nextVerseCoords !== null) {
            currentVerseCoords = nextVerseCoords;
            isCurrentVerseLinkCopied = false;
            containerEl.scrollIntoView();
        }
    }

    async function handleSwipe(e: CustomEvent) {
        const swipeDirection: string = e.detail.direction;
        if (swipeDirection !== "left" && swipeDirection !== "right") return;

        if (swipeDirection === "left" && nextVerseCoords === null) return;
        if (swipeDirection === "right" && prevVerseCoords === null) return;

        if (swipeDirection == "left") nextVerse();
        else prevVerse();
    }

    onDestroy(textSourcesConfigStoreUnsubscribe);
</script>

<Keydown on:ArrowRight={nextVerse} on:ArrowLeft={prevVerse} />
<div
    class="container"
    bind:this={containerEl}
    use:swipe={{ timeframe: 300, minSwipeDistance: 60, touchAction: "pan-y" }}
    on:swipe={handleSwipe}
>
    <p class="verse-nav">
        {#if navigable}
            <span class="icon-button verse-nav-element" on:click={() => prevVerse()} on:keyup={() => {}}>
                <Icon
                    heightEm={0.8}
                    icon="chevron-left"
                    color={prevVerseCoords !== null ? "var(--theme-color-secondary-text)" : "transparent"}
                />
            </span>
        {/if}
        <span class="verse-number verse-nav-element">
            {lookupBookInfo(sectionMetadata, bookNoByParsha(parsha.parsha, sectionMetadata)).bookInfo.name[
                $textSourcesConfigStore[sk].main
            ]}
            {verseCoords2String(currentVerseCoords)}
        </span>
        {#if navigable}
            <span class="icon-button verse-nav-element" on:click={() => nextVerse()} on:keyup={() => {}}>
                <Icon
                    heightEm={0.8}
                    icon="chevron-right"
                    color={nextVerseCoords !== null ? "var(--theme-color-secondary-text)" : "transparent"}
                />
            </span>
        {/if}
        <span
            class="icon-button verse-nav-element"
            on:click={() => {
                const url = `${window.location.origin}${versePath(parsha.parsha, currentVerseCoords)}`;
                navigator.clipboard.writeText(url);
                isCurrentVerseLinkCopied = true;
            }}
            on:keyup={() => {}}
        >
            <Icon
                heightEm={0.8}
                icon={isCurrentVerseLinkCopied ? "check" : "link"}
                color="var(--theme-color-secondary-text)"
            />
        </span>
    </p>
    {#each textSources as textSource}
        <VerseTextBadge
            textId={currentVerseData.text_ids[textSource]}
            text={currentVerseData.text[textSource]}
            {textSource}
        />
    {/each}
    <VerseComments verseData={currentVerseData} on:commentStarToggled={onCommentStarToggled} />
</div>

<style>
    .container {
        padding: 1rem;
        margin-bottom: 1em;
    }

    p {
        margin: 0.2em 0 0.1em 0;
    }

    p.verse-nav {
        display: inline-flex;
        align-items: baseline;
    }

    span.verse-nav-element {
        margin-right: 0.5em;
    }

    span.icon-button {
        display: flex;
        align-items: baseline;
        cursor: pointer;
    }

    span.icon-button:hover {
        background-image: radial-gradient(closest-side, var(--theme-color-secondary-background), transparent);
    }

    span.verse-number {
        color: var(--theme-color-secondary-text);
    }
</style>
