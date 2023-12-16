<script lang="ts">
    import { onDestroy } from "svelte";
    import { editText } from "../api";
    import { isEditingStore } from "../editing";
    import { isHebrewTextSource } from "../utils";
    import Hoverable from "./shared/Hoverable.svelte";
    import { Format } from "../types";

    export let textId: string;
    export let text: string;
    export let textSource: string;
    export let textFormat: Format;

    let isHovering = false;
    let isEditing = false;
    let editedText: string = "";

    const isEditingStoreUnsubscribe = isEditingStore.subscribe((newIsEditing) => {
        if (!newIsEditing) {
            isEditing = false;
        } else if (isHovering) {
            isEditing = true;
            editedText = text;
        }
    });

    async function saveEditedText() {
        text = editedText;
        isEditingStore.set(false);
        isHovering = false;
        await editText({
            id: textId,
            text: editedText,
        });
    }

    onDestroy(isEditingStoreUnsubscribe);
</script>

<span style={isHebrewTextSource(textSource) ? "text-align: right; font-size: x-large;" : ""}>
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
            {#if textFormat == Format.PLAIN}
                {text}
            {:else if textFormat === Format.HTML}
                {@html text}
            {/if}
        {/if}
    </Hoverable>
</span>

<style>
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
