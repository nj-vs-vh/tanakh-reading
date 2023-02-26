<script lang="ts">
    import { getContext, onDestroy } from "svelte";
    import Icon from "./shared/Icon.svelte";

    import type { CommentData, Metadata } from "../types";
    import { CommentFormat } from "../types";
    import { editComment, CommentCoords, starComment, unstarComment } from "../api";
    import Hoverable from "./shared/Hoverable.svelte";
    import { isEditingStore } from "../editing";

    const metadata: Metadata = getContext("metadata");
    export let commentData: CommentData;

    let commentCoords: CommentCoords;
    let isStarred: boolean;
    let editedAnchorPhrase: string;
    let editedCommentText: string;
    $: {
        commentCoords = {
            comment_id: commentData.id,
        };
        isStarred = commentData.is_starred_by_me === true;
    }

    let isLoggedIn = metadata.logged_in_user !== null;
    let isHovering = false;
    let isEditing = false;
    const isEditingStoreUnsubscribe = isEditingStore.subscribe((newIsEditing) => {
        if (!newIsEditing) {
            isEditing = false;
        } else if (isHovering) {
            isEditing = true;
            editedAnchorPhrase = commentData.anchor_phrase;
            editedCommentText = commentData.comment;
        }
    });

    async function toggleStarred() {
        if (!isLoggedIn) return;

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

    async function saveEditedComment() {
        commentData.anchor_phrase = editedAnchorPhrase.length > 0 ? editedAnchorPhrase : null;
        commentData.comment = editedCommentText;
        isEditingStore.set(false);
        isHovering = false;
        await editComment({
            comment_id: commentCoords.comment_id,
            edited_comment: {
                anchor_phrase: commentData.anchor_phrase,
                comment: commentData.comment,
            },
        });
    }

    onDestroy(isEditingStoreUnsubscribe);
</script>

<Hoverable bind:isHovering>
    <div class="comment-body-container">
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
        {#if isEditing}
            <div class="edited-comment-body">
                <input type="text" bind:value={editedAnchorPhrase} />
                <textarea bind:value={editedCommentText} />
                <div>
                    <button on:click={() => isEditingStore.set(false)}>Отмена</button>
                    <button style="background-color: #e1efe1;" on:click={saveEditedComment}>Сохранить</button>
                </div>
            </div>
        {:else}
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
        {/if}
    </div>
</Hoverable>

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

    div.edited-comment-body {
        display: flex;
        flex-direction: column;
        width: 100%;
    }

    div.edited-comment-body > * {
        margin: 0.2em 0;
    }

    div.edited-comment-body > input[type="text"] {
        font-weight: 600;
    }

    div.edited-comment-body > textarea {
        resize: vertical;
        min-height: 5em;
        padding: 0.3em;
    }
</style>
