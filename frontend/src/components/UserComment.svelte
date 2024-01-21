<script lang="ts">
    import { createEventDispatcher, getContext } from "svelte";
    import type { DisplayedUserComment, MultisectionMetadata } from "../types";
    import CommentText from "./shared/CommentText.svelte";
    import { renderTimestamp } from "../utils";
    import Icon from "./shared/Icon.svelte";
    import { deleteUserComment } from "../api";
    import Hoverable from "./shared/Hoverable.svelte";

    const metadata: MultisectionMetadata = getContext("metadata");
    export let comment: DisplayedUserComment;

    const dispatch = createEventDispatcher<{ deleted: { id: string } }>();

    async function deleteComment() {
        await deleteUserComment(comment.db_id);
        dispatch("deleted", { id: comment.db_id });
    }

    let isHovering = false;
</script>

<Hoverable bind:isHovering>
    <div class="comment">
        <span class="comment-header">
            <span class="comment-header-left">
                <span class="author-name">{comment.author_user_data.full_name}</span>
                <span>@{comment.author_username}</span>
                ·
                <span>{renderTimestamp(comment.timestamp)}</span>
            </span>
            {#if isHovering && comment.author_username === metadata.logged_in_user?.username}
                <span style="cursor: pointer" on:click={deleteComment} on:keydown={deleteComment}>
                    <Icon icon="trash" heightEm={0.9} color={"var(--theme-color-secondary-text)"} />
                </span>
            {/if}
        </span>
        <CommentText id={comment.db_id} anchorPhrase={comment.anchor_phrase} comment={comment.comment} isHtml={false} />
    </div>
    </Hoverable
>

<style>
    div.comment {
        display: flex;
        flex-direction: column;
        margin-top: 0.4em;
        margin-bottom: 0.4em;
    }

    span.comment-header {
        color: var(--theme-color-secondary-text);
        font-size: small;
        margin-bottom: 0.2em;
        display: flex;
        flex-direction: row;
        align-items: baseline;
        justify-content: space-between;
    }

    span.author-name {
        color: var(--theme-color-text_tinted);
        margin-right: 0.2em;
    }
</style>
