<script lang="ts">
    import { getContext, setContext } from "svelte";

    import type { FoundMatch } from "../api";
    import VerseComment from "./VerseComment.svelte";
    import VerseText from "./VerseText.svelte";
    import {
        toSingleSection,
        type MultisectionMetadata,
        type SectionKey,
        type SectionMetadata,
        type TextCoords,
    } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";
    import { bookNoByParsha, findParshaSectionKey, lookupBookInfo, versePath } from "../utils";
    import VerseDetailsModal from "./VerseDetailsModal.svelte";
    import Icon from "./shared/Icon.svelte";

    export let match: FoundMatch;
    // if the match contains comment, this flag allows to make it starrable or not
    export let isCommentStarrable: boolean = true;
    // add icon specifying text / comment
    export let addTextCommentIcon: boolean = true;

    const metadata: MultisectionMetadata = getContext("metadata");

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
    let parshaLinkColor = "var(--theme-color-secondary-text)";
    let parshaLinkSizeEm = 0.7;

    // figured out dynamically based on match section
    let sectionKey: SectionKey;
    let sectionMetadata: SectionMetadata;

    const openVerseDetailsModal = () =>
        open(VerseDetailsModal, {
            parsha: match.parsha_data,
            chapter: textCoords.chapter,
            verse: textCoords.verse,
            navigable: false,
        });

    $: {
        textCoords = match.comment !== null ? match.comment.text_coords : match.text.text_coords;

        // find section-specific stuff based on match's text coords, and set contexts for children
        sectionKey = findParshaSectionKey(metadata, textCoords.parsha);
        sectionMetadata = toSingleSection(metadata, sectionKey);
        setContext("sectionKey", sectionKey);
        setContext("sectionMetadata", sectionMetadata);

        let bookName = lookupBookInfo(sectionMetadata, bookNoByParsha(textCoords.parsha, sectionMetadata)).bookInfo
            .name;
        textCoordsStr = `${bookName[$textSourcesConfigStore[sectionKey].main]} ${textCoords.chapter}:${
            textCoords.verse
        }`;
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
                {#if addTextCommentIcon}
                    <Icon icon="tanakh-book" heightEm={1} />
                {/if}
                <span style={addTextCommentIcon ? "margin-left: 0.4em" : ""}>
                    {sectionMetadata.section.comment_sources.find((cs) => cs.key == match.comment.comment_source).name} к
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
                is_starred_by_me: match.comment.is_starred,
            }}
            isStarrable={isCommentStarrable}
        />
    {:else}
        <div class="match-header">
            <span class="text-with-icon">
                {#if addTextCommentIcon}
                    <Icon icon="torah-scroll" heightEm={1} />
                {/if}
                <span style={addTextCommentIcon ? "margin-left: 0.4em" : ""}>
                    <button on:click={openVerseDetailsModal} on:keypress={openVerseDetailsModal}>{textCoordsStr}</button
                    >
                    {sectionMetadata.section.text_sources.find((ts) => ts.key === match.text.text_source).mark}
                </span>
            </span>
            <a href={parshaHref} target="_blank" rel="noreferrer">
                <Icon icon="external-link" heightEm={parshaLinkSizeEm} color={parshaLinkColor} />
            </a>
        </div>
        <VerseText
            textId={match.text.db_id}
            text={match.text.text}
            textSource={match.text.text_source}
            textFormat={match.text.format}
        />
    {/if}
</div>

<style>
    div.match-header {
        color: var(--theme-color-secondary-text);
        margin: 0.4em 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    span.text-with-icon {
        display: flex;
        align-items: center;
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
