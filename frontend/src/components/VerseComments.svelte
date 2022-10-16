<script lang="ts">
    import type { Metadata } from "../types";
    import { CommentFormat } from "../types";
    import { getContext } from "svelte";
    import type { VerseData } from "../types";
    import { commentSourceFlagsStore } from "../settings/commentSources";
    import type { CommentSourceFlags } from "../settings/commentSources";

    let commentSourceFlags: CommentSourceFlags;
    commentSourceFlagsStore.subscribe((v) => {
        commentSourceFlags = v;
    });

    export let verseData: VerseData;

    const metadata: Metadata = getContext("metadata");
    const commenterNames = metadata.commenter_names;
</script>

<div class="container">
    {#each Object.entries(verseData.comments) as [commenter, comments]}
        {#if commentSourceFlags[commenter]}
            <p class="commenter-name">{commenterNames[commenter]}</p>
            {#each comments as commentData}
                <p>
                    {#if commentData.anchor_phrase !== null}
                        <b>{commentData.anchor_phrase}</b>
                        <span>—</span>
                    {/if}
                    {#if commentData.format == CommentFormat.HTML}
                        <span class="html-wrapper">{@html commentData.comment}</span>
                    {:else}
                        <span>{commentData.comment}</span>
                    {/if}
                </p>
            {/each}
        {/if}
    {/each}
</div>

<style>
    .container {
        margin: 0.2em;
    }

    p {
        margin: 0.2em 0 0.1em 0;
    }

    p.commenter-name {
        margin-top: 0.7em;
        font-style: italic;
    }

</style>
