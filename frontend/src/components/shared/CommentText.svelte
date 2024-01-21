<script lang="ts">
    import FoldedOverflow from "./FoldedOverflow.svelte";

    export let id: string;
    export let anchorPhrase: string | null;
    export let comment: string;
    export let isHtml: boolean;
</script>

<p class="comment-text">
    <FoldedOverflow {id}>
        <!-- <span>{commentData.id}</span> -->
        {#if anchorPhrase !== null}
            <strong>{anchorPhrase}</strong>
            <span>—</span>
        {/if}
        {#if isHtml}
            <span class="html-wrapper">{@html comment}</span>
        {:else}
            <span>{comment}</span>
        {/if}
    </FoldedOverflow>
</p>

<style>
    p.comment-text {
        margin: 0;
        white-space: pre-line;
    }
    .html-wrapper > p {
        margin: 0;
        margin-top: 0.5em;
    }
</style>
