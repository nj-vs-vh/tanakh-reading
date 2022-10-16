<script lang="ts">
    import Keydown from "svelte-keydown";
    import {
        TextSource,
        ParshaData,
        VerseData,
        textSourceShort,
    } from "../types";
    import { commentSourceFlagsStore } from "../settings/commentSources";
    import type { CommentSourceFlags } from "../settings/commentSources";
    import VerseComments from "./VerseComments.svelte";
    import InlineIcon from "./shared/InlineIcon.svelte";
    import Icon from "./shared/Icon.svelte";
    import { textSourcesConfigStore } from "../settings/textSources";

    let commentSourceFlags: CommentSourceFlags;
    commentSourceFlagsStore.subscribe((v) => {
        commentSourceFlags = v;
    });

    let textSources: Array<TextSource>;

    textSourcesConfigStore.subscribe((config) => {
        textSources = [];
        textSources.push(config.main);
        for (const [source, isEnabled] of Object.entries(
            config.enabledInDetails
        )) {
            if (isEnabled && source != config.main) textSources.push(source);
        }
    });

    export let parsha: ParshaData;
    export let verse: number;
    export let chapter: number;

    interface VerseCoords {
        chapter: number;
        verse: number;
    }

    let currentVerseCoords: VerseCoords = { chapter: chapter, verse: verse };

    function findVerseCoords(
        chapterNo: number,
        verseNo: number
    ): VerseCoords | null {
        // console.log(chapterNo, verseNo);
        const chapterData = parsha.chapters.find(
            (ch) => ch.chapter === chapterNo
        );
        if (chapterData === undefined) return null;
        let verseData: VerseData | null = null;
        if (verseNo >= 0)
            verseData = chapterData.verses.find((vd) => vd.verse === verseNo);
        // support for Python-like negative verse index
        else
            verseData = chapterData.verses.find(
                (vd) =>
                    vd.verse ===
                    Math.max.apply(
                        Math,
                        chapterData.verses.map((v) => v.verse)
                    ) +
                        verseNo +
                        1
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

        prevVerseCoords = findVerseCoords(
            currentVerseCoords.chapter,
            currentVerseCoords.verse - 1
        );
        if (prevVerseCoords === null)
            prevVerseCoords = findVerseCoords(
                currentVerseCoords.chapter - 1,
                -1
            );
        nextVerseCoords = findVerseCoords(
            currentVerseCoords.chapter,
            currentVerseCoords.verse + 1
        );
        if (nextVerseCoords === null)
            nextVerseCoords = findVerseCoords(
                currentVerseCoords.chapter + 1,
                1
            );
    }

    function prevVerse() {
        if (prevVerseCoords !== null) currentVerseCoords = prevVerseCoords;
    }

    function nextVerse() {
        if (nextVerseCoords !== null) currentVerseCoords = nextVerseCoords;
    }
</script>

<Keydown on:ArrowRight={nextVerse} on:ArrowLeft={prevVerse} />
<div class="container">
    <p class="verse-nav">
        <span
            class="arrow-container"
            on:click={(e) => prevVerse()}
            on:keyup={(e) => {}}
        >
            <InlineIcon heightEm={0.8}>
                <Icon
                    icon="chevron-left"
                    color={prevVerseCoords !== null ? "grey" : "white"}
                />
            </InlineIcon>
        </span>
        <span class="verse-number">
            {currentVerseCoords.chapter}:{currentVerseData.verse}
        </span>
        <span
            class="arrow-container"
            on:click={(e) => nextVerse()}
            on:keyup={(e) => {}}
        >
            <InlineIcon heightEm={0.8}>
                <Icon
                    icon="chevron-right"
                    color={nextVerseCoords !== null ? "grey" : "white"}
                />
            </InlineIcon>
        </span>
    </p>
    {#each textSources as textSource}
        <div class="verse-text-container">
            <blockquote>
                {currentVerseData.text[textSource]}
            </blockquote>
            <span>
                {textSourceShort.get(textSource)}
            </span>
        </div>
    {/each}
    <VerseComments verseData={currentVerseData} />
</div>

<style>
    .container {
        max-width: 60vw;
        margin: 0.3em 1em 0.3em 0.3em;
    }

    p {
        margin: 0.2em 0 0.1em 0;
    }

    p.verse-nav {
        display: inline-flex;
        align-items: center;
    }

    span.arrow-container {
        display: flex;
        align-items: baseline;
        cursor: pointer;
    }

    span.arrow-container:hover {
        background-image: radial-gradient(
            closest-side,
            rgb(221, 221, 221),
            transparent
        );
    }

    span.verse-number {
        color: grey;
        margin: 0 0.5em;
    }

    blockquote {
        margin: 0.1em;
        padding: 0.1em 0.1em 0.1em 0.5em;
        border-left: solid rgb(179, 179, 179) 2px;
        color: rgb(68, 68, 68);
        max-width: 90%;
    }

    .verse-text-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 0.3em 0.5em 0.9em 0.1em;
        color: grey;
    }
</style>
