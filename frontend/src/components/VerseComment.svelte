<script lang="ts">
    import { createEventDispatcher, getContext, onDestroy } from "svelte";

    import Hoverable from "./shared/Hoverable.svelte";
    import FoldedOverflow from "./shared/FoldedOverflow.svelte";
    import Icon from "./shared/Icon.svelte";

    import type { CommentData, CommentStarToggledEvent, SectionMetadata } from "../types";
    import { CommentFormat } from "../types";
    import { editComment, CommentCoords, starComment, unstarComment } from "../api";
    import { isEditingStore } from "../editing";

    const sectionMetadata: SectionMetadata = getContext("sectionMetadata");
    export let commentData: CommentData;
    export let isStarrable: boolean = true;

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

    let isLoggedIn = sectionMetadata.logged_in_user !== null;
    let isHovering = false;
    let isEditing = false;
    const isEditingStoreUnsubscribe = isEditingStore.subscribe((newIsEditing) => {
        if (!newIsEditing) {
            isEditing = false;
        } else if (isHovering) {
            isEditing = true;
            editedAnchorPhrase = commentData.anchor_phrase === null ? "" : commentData.anchor_phrase;
            editedCommentText = commentData.comment;
        }
    });

    let toggleStarredRunning = false;

    const dispatch = createEventDispatcher<{ commentStarToggled: CommentStarToggledEvent }>();

    async function toggleStarred() {
        if (toggleStarredRunning) return; // preventing double-click race condition issues
        if (!isLoggedIn) return;

        try {
            toggleStarredRunning = true;

            // first updating the UI
            const originalIsStarred = isStarred;
            isStarred = !isStarred;
            commentData.is_starred_by_me = isStarred;

            dispatch("commentStarToggled", { commentId: commentCoords.comment_id, newIsStarred: isStarred });

            // then syncing with backend
            if (originalIsStarred) {
                await unstarComment(commentCoords);
            } else {
                await starComment(commentCoords);
            }
        } finally {
            toggleStarredRunning = false;
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
            {#if isLoggedIn && isStarrable}
                <div class="clickable-icon" on:click={toggleStarred} on:keydown={toggleStarred}>
                    <Icon
                        icon="bookmark"
                        color={isStarred
                            ? "var(--theme-color-bookmark-active)"
                            : isHovering
                            ? "var(--theme-color-bookmark-potential)"
                            : "transparent"}
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
                <FoldedOverflow id={commentData.id}>
                    <!-- <span>{commentData.id}</span> -->
                    {#if commentData.anchor_phrase !== null}
                        <strong>{commentData.anchor_phrase}</strong>
                        <span>—</span>
                    {/if}
                    {#if commentData.format == CommentFormat.HTML}
                        <span class="html-wrapper">{@html commentData.comment}</span>
                    {:else}
                        <span>{commentData.comment}</span>
                    {/if}
                </FoldedOverflow>
            </p>
        {/if}
    </div>
</Hoverable>

<style>
    .comment-body-container {
        margin-top: 0.3em;
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

    .html-wrapper > p {
        margin: 0;
        margin-top: 0.5em;
    }
</style>
