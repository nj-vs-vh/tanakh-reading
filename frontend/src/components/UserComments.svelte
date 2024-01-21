<script lang="ts">
    import { createEventDispatcher, getContext } from "svelte";
    import type { DisplayedUserComment, MultisectionMetadata, TextCoords, UserCommentEvent } from "../types";
    import { createUserComment } from "../api";
    import UserComment from "./UserComment.svelte";

    const dispatch = createEventDispatcher<{ userCommentAction: UserCommentEvent }>();

    const metadata: MultisectionMetadata = getContext("metadata");
    export let userComments: Array<DisplayedUserComment> | undefined;
    export let textCoords: TextCoords;
    export let isAddingNewComment: boolean = false;

    if (userComments === undefined) {
        userComments = [];
    }

    userComments.sort((c1, c2) => Date.parse(c1.timestamp) - Date.parse(c2.timestamp));

    let newCommentText = "";
    let isSaving = false;

    async function saveNewComment() {
        if (newCommentText.length === 0) return;
        try {
            isSaving = true;
            const newCommentStored = await createUserComment({
                text_coords: textCoords,
                anchor_phrase: null,
                comment: newCommentText,
            });
            const newCommentDisplayed = newCommentStored as DisplayedUserComment;
            newCommentDisplayed.author_user_data = metadata.logged_in_user.data;
            userComments = [...userComments, newCommentDisplayed];
            newCommentText = "";
            isAddingNewComment = false;
            dispatch("userCommentAction", {
                chapter: textCoords.chapter,
                verse: textCoords.verse,
                userCommentId: newCommentStored.db_id,
                action: "created",
            });
        } catch (e) {
            console.error(`Error creating user comment: ${e}`);
            isSaving = false;
        }
    }

    function initTextArea(el: HTMLElement) {
        if (isAddingNewComment) {
            el.focus();
        }
    }
</script>

{#if isAddingNewComment || (userComments !== undefined && userComments.length > 0)}
    <div class="container">
        {#each userComments as comment}
            <UserComment
                {comment}
                on:deleted={(e) => {
                    userComments = userComments.filter((c) => c.db_id != e.detail.id);
                    dispatch("userCommentAction", {
                        chapter: textCoords.chapter,
                        verse: textCoords.verse,
                        userCommentId: e.detail.id,
                        action: "deleted",
                    });
                }}
            />
        {/each}
        {#if isAddingNewComment}
            <div class="new-comment">
                <textarea
                    placeholder="..."
                    bind:value={newCommentText}
                    use:initTextArea
                    on:focus={() => {
                        isAddingNewComment = true;
                    }}
                    on:input={(e) => {
                        let ta = e.target;
                        if (newCommentText.length == 0) {
                            // @ts-ignore
                            ta.style.height = "0px"; // reset to min-height (see css)
                            setTimeout(() => {
                                if (isAddingNewComment && newCommentText.length == 0) {
                                    isAddingNewComment = false;
                                }
                            }, 10000);
                        } else {
                            // auto-resize adapted from https://stackoverflow.com/questions/454202/creating-a-textarea-with-auto-resize
                            // @ts-ignore
                            ta.style.height = "auto";
                            // @ts-ignore
                            ta.style.height = `${ta.scrollHeight}px`;
                        }
                    }}
                />
                {#if isAddingNewComment}
                    <button disabled={isSaving || newCommentText.length === 0} on:click={saveNewComment}
                        >{isSaving ? "Сохранение..." : "Сохранить"}</button
                    >
                    <button
                        on:click={() => {
                            isAddingNewComment = false;
                        }}>Отмена</button
                    >
                {/if}
            </div>
        {/if}
    </div>
{/if}

<style>
    div.container {
        margin: 0.2em;
        margin-bottom: 0.6em;
        padding-bottom: 0.6em;
        border-bottom: 1px solid var(--theme-color-secondary-border);
    }

    div.new-comment {
        margin-top: 0.6em;
    }

    textarea {
        width: 100%;
        resize: none;
        min-height: 1.4em;
        padding: 0.2em;
        border: none;
        background: var(--theme-color-secondary-background);
        color: var(--theme-color-text);
        outline: none;
        font-family: "verdana", "Times New Roman", Times, serif;
        font-size: inherit;
    }
</style>
