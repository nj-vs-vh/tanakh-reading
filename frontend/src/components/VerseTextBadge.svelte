<script lang="ts">
    import { getContext } from "svelte";
    import type { Format, SectionMetadata } from "../types";

    import VerseText from "./VerseText.svelte";

    const sectionMetadata: SectionMetadata = getContext("sectionMetadata");

    export let textId: string;
    export let text: string;
    export let textSource: string;
    export let textFormat: Format;
</script>

<div class="verse-text-container">
    <blockquote>
        <VerseText {textId} {text} {textSource} {textFormat} />
    </blockquote>
    <span class="verse-text-source-mark">
        {sectionMetadata.section.text_sources.find(ts => ts.key === textSource).mark}
    </span>
</div>

<style>
    blockquote {
        margin: 0.1em;
        padding: 0.1em 0.1em 0.1em 0.5em;
        border-left: solid var(--theme-color-secondary-border) 2px;
        color: var(--theme-color-text_tinted);
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
        color: var(--theme-color-secondary-text);
    }
</style>
