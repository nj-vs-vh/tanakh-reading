<script lang="ts">
    import { getContext } from "svelte";

    import type { FoundMatch } from "../api";
    import VerseComment from "./VerseComment.svelte";
    import VerseText from "./VerseText.svelte";
    import type { Metadata } from "../types";

    export let match: FoundMatch;

    const metadata: Metadata = getContext("metadata");

    let textCoords = match.comment !== null ? match.comment.text_coords : match.text.text_coords;
    let textCoordsStr = `${textCoords.chapter}:${textCoords.verse}`;
    let matchHeaderText =
        match.comment !== null
            ? `${metadata.commenter_names[match.comment.comment_source]}, комментарий к `
            : match.text.text_coords;
</script>

{#if match.comment !== null}
    <VerseComment
        commentData={{
            id: match.comment.id,
            anchor_phrase: match.comment.anchor_phrase,
            comment: match.comment.comment,
            format: match.comment.format,
        }}
    />
{:else}
    <VerseText textId={match.text.id} text={match.text.text} textSource={match.text.text_source} />
{/if}
