<script lang="ts">
    import { getContext, onDestroy } from "svelte";
    import Keydown from "svelte-keydown";
    import { swipe } from "svelte-gestures";
    import type { Metadata, ParshaData, VerseData } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";
    import VerseComments from "./VerseComments.svelte";
    import Icon from "./shared/Icon.svelte";
    import { areInsideVerseCoordsList, getVerseCoords, VerseCoords, versePath, verseCoords2string } from "../utils";
    import { isEditingStore } from "../editing";

    const metadata: Metadata = getContext("metadata");

    let textSources: Array<string>;

    const textSourcesConfigStoreUnsubscribe = textSourcesConfigStore.subscribe((config) => {
        textSources = [];
        textSources.push(config.main);
        for (const [source, isEnabled] of Object.entries(config.enabledInDetails)) {
            if (isEnabled && source != config.main) textSources.push(source);
        }
    });

    export let parsha: ParshaData;
    const parshaVerseCoords = getVerseCoords(parsha);

    export let verse: number;
    export let chapter: number;

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

<Keydown
    on:ArrowRight={nextVerse}
    on:ArrowLeft={prevVerse}
    on:combo={(e) => {
        // console.log(`Current store value: ${$isEditingStore}`);
        if (metadata.logged_in_user !== null && metadata.logged_in_user.is_editor && e.detail === "Control-q") {
            isEditingStore.set(true);
        } else {
            // console.log(`Ignored combo: ${e.detail}`);
        }
    }}
/>
<div
    class="container"
    bind:this={containerEl}
    use:swipe={{ timeframe: 300, minSwipeDistance: 60, touchAction: "pan-y" }}
    on:swipe={handleSwipe}
>
    <p class="verse-nav">
        <span class="icon-button verse-nav-element" on:click={(e) => prevVerse()} on:keyup={(e) => {}}>
            <Icon heightEm={0.8} icon="chevron-left" color={prevVerseCoords !== null ? "grey" : "white"} />
        </span>
        <span class="verse-number verse-nav-element">
            {verseCoords2string(currentVerseCoords)}
        </span>
        <span class="icon-button verse-nav-element" on:click={(e) => nextVerse()} on:keyup={(e) => {}}>
            <Icon heightEm={0.8} icon="chevron-right" color={nextVerseCoords !== null ? "grey" : "white"} />
        </span>
        <span
            class="icon-button verse-nav-element"
            on:click={(e) => {
                const url = `${window.location.origin}${versePath(parsha.parsha, currentVerseCoords)}`;
                navigator.clipboard.writeText(url);
                isCurrentVerseLinkCopied = true;
            }}
            on:keyup={(e) => {}}
        >
            <Icon heightEm={0.8} icon={isCurrentVerseLinkCopied ? "check" : "link"} color="grey" />
        </span>
    </p>
    {#each textSources as textSource}
        <div class="verse-text-container">
            <blockquote>
                {currentVerseData.text[textSource]}
            </blockquote>
            <span class="verse-text-source-mark">
                {metadata.text_source_marks[textSource]}
            </span>
        </div>
    {/each}
    <VerseComments verseData={currentVerseData} parsha={parsha.parsha} chapter={currentVerseCoords.chapter} />
</div>

<style>
    .container {
        padding: 1rem;
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
        background-image: radial-gradient(closest-side, rgb(221, 221, 221), transparent);
    }

    span.verse-number {
        color: grey;
    }

    blockquote {
        margin: 0.1em;
        padding: 0.1em 0.1em 0.1em 0.5em;
        border-left: solid rgb(179, 179, 179) 2px;
        color: rgb(68, 68, 68);
        max-width: 90%;
    }

    span.verse-text-source-mark {
        padding-left: 0.2em;
    }

    .verse-text-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 0.3em 0.5em 0.9em 0.1em;
        color: grey;
    }
</style>
