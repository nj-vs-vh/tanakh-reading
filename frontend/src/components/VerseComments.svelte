<script lang="ts">
    import type { SectionKey, SectionMetadata } from "../types";
    import { getContext } from "svelte";
    import type { VerseData } from "../types";
    import { commentSourcesConfigStore, CommentFilterByBookmarkMode } from "../settings/commentSources";
    import VerseComment from "./VerseComment.svelte";
    import { commentPassesFilters } from "../utils";

    export let verseData: VerseData;

    const sectionMetadata: SectionMetadata = getContext("sectionMetadata");
    const sk: SectionKey = getContext("sectionKey");
    const commenterNames = Object.fromEntries(sectionMetadata.section.comment_sources.map((cs) => [cs.key, cs.name]));
</script>

<div class="container">
    {#each $commentSourcesConfigStore[sk].sourcesOrder as commentSource}
        {#if verseData.comments[commentSource] !== undefined && verseData.comments[commentSource]
                .map( (commentData) => commentPassesFilters(commentData, commentSource, $commentSourcesConfigStore[sk]), )
                .reduce((a, b) => a || b, false)}
            <div class="comments-block">
                <p class="comment-source-name">{commenterNames[commentSource]}</p>
                {#each verseData.comments[commentSource] as commentData}
                    {#if // prettier-ignore
                    $commentSourcesConfigStore[sk].filterByBookmarkMode === CommentFilterByBookmarkMode.NONE
                    || (
                        $commentSourcesConfigStore[sk].filterByBookmarkMode === CommentFilterByBookmarkMode.MY
                        && commentData.is_starred_by_me === true
                    )}
                        <div class="comment-container">
                            <VerseComment {commentData} on:commentStarToggled />
                        </div>
                    {/if}
                {/each}
            </div>
        {/if}
    {/each}
</div>

<style>
    div.container {
        margin: 0.2em;
    }

    p.comment-source-name {
        color: var(--theme-color-secondary-text);
        margin-bottom: 0.4em;
        margin-top: 0;
    }

    div.comments-block {
        padding: 0.8em 0;
        border-bottom: 1px var(--theme-color-secondary-border) solid;
    }

    div.comments-block:first-of-type {
        padding-top: 0;
    }

    div.comments-block:last-of-type {
        padding-bottom: 0;
        border-bottom: none;
    }

    div.comment-container {
        margin-top: 0.4em;
    }
</style>
