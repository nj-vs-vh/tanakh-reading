<script lang="ts">
    import { getContext } from "svelte";

    import type { FoundMatch } from "../api";
    import VerseComment from "./VerseComment.svelte";
    import VerseText from "./VerseText.svelte";
    import type { Metadata, TextCoords } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";
    import { bookNoByParsha } from "../utils";
    import VerseDetailsModal from "./VerseDetailsModal.svelte";

    export let match: FoundMatch;

    const metadata: Metadata = getContext("metadata");

    // @ts-ignore
    const { open, close } = getContext("simple-modal");

    window.addEventListener("popstate", () => {
        try {
            close();
        } catch (e) {}
    });

    let textCoords: TextCoords;
    let textCoordsStr: string;

    const openVerseDetailsModal = () =>
        open(VerseDetailsModal, {
            parsha: match.parsha_data,
            chapter: textCoords.chapter,
            verse: textCoords.verse,
            navigable: false,
        });

    $: {
        textCoords = match.comment !== null ? match.comment.text_coords : match.text.text_coords;
        textCoordsStr = `${
            metadata.book_names[bookNoByParsha(textCoords.parsha, metadata)][$textSourcesConfigStore.main]
        } ${textCoords.chapter}:${textCoords.verse}`;
    }
</script>

<div>
    {#if match.comment !== null}
        <div class="match-header">
            {metadata.commenter_names[match.comment.comment_source]}, комментарий к
            <button on:click={openVerseDetailsModal} on:keypress={openVerseDetailsModal}>{textCoordsStr}</button>
        </div>
        <VerseComment
            commentData={{
                id: match.comment.db_id,
                anchor_phrase: match.comment.anchor_phrase,
                comment: match.comment.comment,
                format: match.comment.format,
            }}
        />
    {:else}
        <div class="match-header">
            <button on:click={openVerseDetailsModal} on:keypress={openVerseDetailsModal}>{textCoordsStr}</button>
            {metadata.text_source_marks[match.text.text_source]}
        </div>
        <VerseText textId={match.text.db_id} text={match.text.text} textSource={match.text.text_source} />
    {/if}
</div>

<style>
    div.match-header {
        color: rgb(80, 80, 80);
        margin: 0.4em 0;
    }

    button {
        cursor: pointer;
        text-decoration: underline;
        border: unset;
        background: unset;
        font-size: inherit;
        padding: unset;
        color: inherit;
    }
</style>
