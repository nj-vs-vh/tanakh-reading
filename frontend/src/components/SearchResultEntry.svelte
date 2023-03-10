<script lang="ts">
    import { getContext } from "svelte";

    import type { FoundMatch } from "../api";
    import VerseComment from "./VerseComment.svelte";
    import VerseText from "./VerseText.svelte";
    import type { Metadata, TextCoords } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";
    import { bookNoByParsha, parshaPath, versePath } from "../utils";
    import VerseDetailsModal from "./VerseDetailsModal.svelte";
    import Icon from "./shared/Icon.svelte";

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
    let parshaHref: string;
    let parshaLinkColor = "rgb(180, 180, 180)";
    let parshaLinkSizeEm = 0.7;

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
        parshaHref = versePath(textCoords.parsha, {
            chapter: textCoords.chapter,
            verse: textCoords.verse,
        });
    }
</script>

<div>
    {#if match.comment !== null}
        <div class="match-header">
            <span class="text-with-icon">
                <Icon icon="tanakh-book" heightEm={1} />
                <span>
                    {metadata.commenter_names[match.comment.comment_source]} к
                    <button on:click={openVerseDetailsModal} on:keypress={openVerseDetailsModal}>{textCoordsStr}</button
                    >
                </span>
            </span>
            <a href={parshaHref} target="_blank" rel="noreferrer">
                <Icon icon="external-link" heightEm={parshaLinkSizeEm} color={parshaLinkColor} />
            </a>
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
            <span class="text-with-icon">
                <Icon icon="torah-scroll" heightEm={1} />
                <span>
                    <button on:click={openVerseDetailsModal} on:keypress={openVerseDetailsModal}>{textCoordsStr}</button
                    >
                    {metadata.text_source_marks[match.text.text_source]}
                </span>
            </span>
            <a href={parshaHref} target="_blank" rel="noreferrer">
                <Icon icon="external-link" heightEm={parshaLinkSizeEm} color={parshaLinkColor} />
            </a>
        </div>
        <VerseText textId={match.text.db_id} text={match.text.text} textSource={match.text.text_source} />
    {/if}
</div>

<style>
    div.match-header {
        color: rgb(80, 80, 80);
        margin: 0.4em 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    span.text-with-icon {
        display: flex;
        align-items: center;
    }

    span.text-with-icon > span {
        margin-left: 0.4em;
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
