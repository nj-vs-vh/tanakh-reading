<script lang="ts">
    import Icon from "./shared/Icon.svelte";

    export let starredCommentsCount: number;
</script>

{#if starredCommentsCount > 0}
    <span class="badge">
        <span class="badge-item">
            <Icon icon="bookmark" color="var(--starred-comment-color)" heightEm={1} />
        </span>
    </span>
{/if}

<style>
    span.badge {
        font-size: xx-small;
        position: relative;
        top: -0.3em;
    }
</style>
