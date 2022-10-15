<script lang="ts">
    import type { Metadata } from "../types";
    import { CommentFormat } from "../types";
    import { getContext } from "svelte";
    import { TextSource, VerseData } from "../types";

    export let verseData: VerseData;
    export let chapter: number;

    const metadata: Metadata = getContext("metadata");
    const commenterNames = metadata.commenter_names;
</script>

<div class="container">
    <p class="verse-number">{chapter}:{verseData.verse}</p>
    <blockquote>
        {verseData.text[TextSource.FG]}
    </blockquote>
    {#each Object.entries(verseData.comments) as [commenter, comments]}
        <p class="commenter-name">{commenterNames[commenter]}</p>
        {#each comments as commentData}
            <p>
                {#if commentData.anchor_phrase !== null}
                    <b>{commentData.anchor_phrase}</b>
                    <span>—</span>
                {/if}
                {#if commentData.format == CommentFormat.HTML}
                    <span>{@html commentData.comment}</span>
                {:else}
                    <span>{commentData.comment}</span>
                {/if}
            </p>
        {/each}
    {/each}
</div>

<style>
    .container {
        max-width: 60vw;
        margin: 0.3em 3em 0.3em 0.3em;
    }

    p {
        margin: 0.2em 0 0.1em 0;
    }

    p.verse-number {
        color: grey;
    }

    p.commenter-name {
        margin-top: 0.7em;
        font-style: italic;
    }

    blockquote {
        margin: 0.3em 0.5em 0.9em 0.1em;
        padding: 0.1em 0.1em 0.1em 0.5em;
        border-left: solid rgb(179, 179, 179) 2px;
        color: rgb(68, 68, 68);
    }
</style>
