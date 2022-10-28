<script lang="ts">
    import { getContext } from "svelte";
    import Icon from "./shared/Icon.svelte";

    import type { CommentData, Metadata } from "../types";
    import { CommentFormat } from "../types";
    import { FullCommentCoords, starComment, unstarComment } from "../api";

    const metadata: Metadata = getContext("metadata");
    export let commentData: CommentData;
    export let parsha: number;
    export let chapter: number;
    export let verse: number;

    let isLoggedIn = metadata.logged_in_user !== null;
    let isHovering = false;
    $: isStarred = commentData.is_starred_by_me === true;

    function setHovering() {
        isHovering = true;
    }
    function unsetHovering() {
        isHovering = false;
    }

    async function toggleStarred() {
        if (!isLoggedIn) return;

        const commentCoords: FullCommentCoords = {
            comment_id: commentData.id,
            parsha: parsha,
            chapter: chapter,
            verse: verse,
        };

        // first updating the UI
        const originalIsStarred = isStarred;
        isStarred = !isStarred;
        commentData.is_starred_by_me = isStarred;

        // then syncing with backend
        if (originalIsStarred) {
            await unstarComment(commentCoords);
        } else {
            await starComment(commentCoords);
        }
    }
</script>

<div
    class="comment-body-container"
    on:mouseover={setHovering}
    on:mouseout={unsetHovering}
    on:focus={setHovering}
    on:blur={unsetHovering}
>
    <div class="icons-container">
        {#if isLoggedIn}
            <div class="clickable-icon" on:click={toggleStarred} on:keydown={toggleStarred}>
                <Icon
                    icon="bookmark"
                    color={isStarred ? "#c6a059" : isHovering ? "rgb(200, 200, 200)" : "transparent"}
                    heightEm={0.7}
                />
            </div>
        {/if}
    </div>
    <p class="comment-text">
        {#if commentData.anchor_phrase !== null}
            <strong>{commentData.anchor_phrase}</strong>
            <span>—</span>
        {/if}
        {#if commentData.format == CommentFormat.HTML}
            <span class="html-wrapper">{@html commentData.comment}</span>
        {:else}
            <span>{commentData.comment}</span>
        {/if}
    </p>
</div>

<style>
    .comment-body-container {
        margin-top: 0.1em;
        display: flex;
        position: relative;
        left: -1em;
    }

    div.icons-container {
        min-width: 1em;
        display: flex;
        flex-direction: column;
        padding-left: 0.1em;
        margin-top: 0.1em;
    }

    p.comment-text {
        margin: 0;
    }

    div.clickable-icon {
        cursor: pointer;
        width: 100%;
    }
</style>
