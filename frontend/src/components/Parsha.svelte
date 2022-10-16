<script lang="ts">
    import { getContext } from "svelte";
    import type { Metadata, ParshaData } from "../types";
    import { TextSource } from "../types";
    import VerseDetails from "./VerseDetailsModal.svelte";
    import InlineIcon from "./shared/InlineIcon.svelte";
    import Icon from "./shared/Icon.svelte";
    import Menu from "./Menu.svelte";

    // @ts-ignore
    const { open } = getContext("simple-modal");

    export let parsha: ParshaData;

    const chapters = parsha.chapters.map((chapterData) => chapterData.chapter);
    chapters.sort();
    const metadata: Metadata = getContext("metadata");
</script>

<Menu homeButton />
<div class="page">
    <div class="container">
        <span class="small-header">
            Книга <b>{metadata.book_names[parsha.book][TextSource.FG]}</b>,
            недельный раздел
            <b>{metadata.parsha_names[parsha.parsha][TextSource.FG]}</b>, главы
            с <b>{chapters[0]}</b> по <b>{chapters[chapters.length - 1]}</b>
        </span>
        {#each parsha.chapters as chapter}
            <h2>Глава {chapter.chapter}</h2>
            {#each chapter.verses as verse}
                <span class="verse-number">{verse.verse}.</span>
                <span class="verse-text">{verse.text[TextSource.FG]}</span>
                {#if Object.keys(verse.comments).length > 0}
                    <span
                        class="clickable-tooltip"
                        on:click={() => open(VerseDetails, { verseData: verse, chapter: chapter.chapter })}
                        on:keydown={() => open(VerseDetails, { verseData: verse, chapter: chapter.chapter })}
                    >
                        <InlineIcon heightEm={0.7}>
                            <Icon icon={'asterisk'} color={"#606060"}/>
                        </InlineIcon>
                    </span>
                {/if}
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
        margin: 4em 0 1em 0;
    }

    span.verse-text {
        margin-right: 0.1em;
    }

    span.clickable-tooltip {
        cursor: pointer;
        margin-right: 0.3em;
    }

    span.verse-number {
        color: grey;
        user-select: none;
        margin-right: 0.2em;
    }

    .small-header {
        font-size: medium;
        font-weight: normal;
        margin: 0;
    }
</style>
