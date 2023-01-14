<script lang="ts">
    import { getContext, onDestroy } from "svelte";
    import { editText } from "../api";
    import { isEditingStore } from "../editing";
    import type { Metadata, VerseData } from "../types";
    import { isHebrewTextSource } from "../utils";
    import Hoverable from "./shared/Hoverable.svelte";

    const metadata: Metadata = getContext("metadata");

    export let verseData: VerseData;
    export let textSource: string;
    export let parsha: number;
    export let chapter: number;
    export let verse: number;

    let isHovering = false;
    let isEditing = false;
    let editedText: string = "";

    const isEditingStoreUnsubscribe = isEditingStore.subscribe((newIsEditing) => {
        if (!newIsEditing) {
            isEditing = false;
        } else if (isHovering) {
            isEditing = true;
            editedText = verseData.text[textSource];
        }
    });

    async function saveEditedText() {
        verseData.text[textSource] = editedText;
        isEditingStore.set(false);
        isHovering = false;
        await editText({
            parsha: parsha,
            chapter: chapter,
            verse: verse,
            translation_key: textSource,
            new_text: editedText,
        });
    }

    onDestroy(isEditingStoreUnsubscribe);
</script>

<Hoverable bind:isHovering>
    {#if isEditing}
        <div class="edited-text">
            <textarea bind:value={editedText} />
            <div>
                <button on:click={() => isEditingStore.set(false)}>Отмена</button>
                <button style="background-color: #e1efe1;" on:click={saveEditedText}>Сохранить</button>
            </div>
        </div>
    {:else}
        <div class="verse-text-container">
            <blockquote style={isHebrewTextSource(textSource) ? "text-align: right;" : ""}>
                {verseData.text[textSource]}
            </blockquote>
            <span class="verse-text-source-mark">
                {metadata.text_source_marks[textSource]}
            </span>
        </div>
    {/if}
</Hoverable>

<style>
    blockquote {
        margin: 0.1em;
        padding: 0.1em 0.1em 0.1em 0.5em;
        border-left: solid rgb(179, 179, 179) 2px;
        color: rgb(68, 68, 68);
        width: 95%;
    }

    span.verse-text-source-mark {
        padding-left: 0.2em;
    }

    .verse-text-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 0.3em 0.5em 0.9em 0.1em;
        color: grey;
    }

    div.edited-text {
        display: flex;
        flex-direction: column;
        width: calc(100% - 1em);
        margin: 0 0.5em;
    }

    div.edited-text > * {
        margin: 0.2em 0;
    }

    div.edited-text > textarea {
        resize: vertical;
        min-height: 5em;
        padding: 0.3em;
    }
</style>
