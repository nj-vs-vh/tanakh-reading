<script lang="ts">
    import { getContext } from "svelte";
    import type { Metadata, ParshaData } from "../types";
    import { TextSource } from "../types";
    import type { VerseData, ChapterData } from "../types";
    import VerseDetails from "./VerseDetailsModal.svelte";
    import InlineIcon from "./shared/InlineIcon.svelte";
    import Icon from "./shared/Icon.svelte";
    import Menu from "./Menu.svelte";
    import { CommentStyle, commentStyleStore } from "../commentStyles";

    const metadata: Metadata = getContext("metadata");

    let commentStyle: CommentStyle;
    commentStyleStore.subscribe((v) => {
        commentStyle = v;
    });

    // @ts-ignore
    const { open } = getContext("simple-modal");
    const openVerseData = (verse: VerseData, chapter: ChapterData) =>
        open(VerseDetails, {
            verseData: verse,
            chapter: chapter.chapter,
        });

    export let parsha: ParshaData;

    const chapters = parsha.chapters.map((chapterData) => chapterData.chapter);
    chapters.sort();
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
                <span
                    class={commentStyle === CommentStyle.CLICKABLE_TEXT
                        ? "verse-text clickable"
                        : "verse-text"}
                    on:click={() => {
                        commentStyle === CommentStyle.CLICKABLE_TEXT
                            ? openVerseData(verse, chapter)
                            : null;
                    }}
                    on:keydown={() => {
                        commentStyle === CommentStyle.CLICKABLE_TEXT
                            ? openVerseData(verse, chapter)
                            : null;
                    }}
                >
                    {verse.text[TextSource.FG]}
                </span>
                {#if commentStyle === CommentStyle.ASTRERISK}
                    <span
                        class="comment-asterisk"
                        on:click={() => openVerseData(verse, chapter)}
                        on:keydown={() => openVerseData(verse, chapter)}
                    >
                        <InlineIcon heightEm={0.7}>
                            <Icon icon={"asterisk"} color={"#606060"} />
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
        margin: 4em 10px 4em 10px;
    }

    span.verse-text {
        margin-right: 0.1em;
    }

    span.comment-asterisk {
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
