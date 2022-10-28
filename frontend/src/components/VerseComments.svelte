<script lang="ts">
    import type { Metadata } from "../types";
    import { getContext } from "svelte";
    import type { VerseData } from "../types";
    import { commentSourceFlagsStore } from "../settings/commentSources";
    import type { CommentSourceFlags } from "../settings/commentSources";
    import VerseComment from "./VerseComment.svelte";

    let commentSourceFlags: CommentSourceFlags;
    commentSourceFlagsStore.subscribe((v) => {
        commentSourceFlags = v;
    });

    export let verseData: VerseData;
    export let parsha: number;
    export let chapter: number;

    const metadata: Metadata = getContext("metadata");
    const commenterNames = metadata.commenter_names;
</script>

<div class="container">
    {#each Object.entries(verseData.comments) as [commenter, comments]}
        {#if commentSourceFlags[commenter]}
            <div class="comments-block">
                <p class="commenter-name">{commenterNames[commenter]}</p>
                {#each comments as commentData}
                    <VerseComment {commentData} {parsha} {chapter} verse={verseData.verse} />
                {/each}
            </div>
        {/if}
    {/each}
</div>

<style>
    .container {
        margin: 0.2em;
    }

    p.commenter-name {
        color: rgb(80, 80, 80);
        margin: 0.3em 0;
    }

    div.comments-block {
        padding: 0.8em 0;
        border-bottom: 1px rgb(189, 189, 189) solid;
    }

    div.comments-block:first-of-type {
        padding-top: 0;
    }

    div.comments-block:last-of-type {
        padding-bottom: 0;
        border-bottom: none;
    }
</style>
