<script lang="ts">
    import { getContext } from "svelte";

    import type { FoundMatch } from "../api";
    import VerseComment from "./VerseComment.svelte";
    import VerseText from "./VerseText.svelte";
    import type { Metadata } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";
    import { bookNoByParsha } from "../utils";

    export let match: FoundMatch;

    const metadata: Metadata = getContext("metadata");

    let matchHeaderText: string;
    $: {
        let textCoords = match.comment !== null ? match.comment.text_coords : match.text.text_coords;
        let bookNo = bookNoByParsha(textCoords.parsha, metadata);
        let textCoordsStr = `${metadata.book_names[bookNo][$textSourcesConfigStore.main]} ${textCoords.chapter}:${
            textCoords.verse
        }`;
        matchHeaderText =
            match.comment !== null
                ? `${metadata.commenter_names[match.comment.comment_source]}, комментарий к ${textCoordsStr}`
                : `${textCoordsStr} ${metadata.text_source_marks[match.text.text_source]}`;
    }
</script>

<div>
    <div class="match-header">
        {matchHeaderText}
    </div>
    {#if match.comment !== null}
        <VerseComment
            commentData={{
                id: match.comment.db_id,
                anchor_phrase: match.comment.anchor_phrase,
                comment: match.comment.comment,
                format: match.comment.format,
            }}
        />
    {:else}
        <VerseText textId={match.text.db_id} text={match.text.text} textSource={match.text.text_source} />
    {/if}
</div>

<style>
    div.match-header {
        color: grey;
        margin-bottom: 0.1em;
    }
</style>
