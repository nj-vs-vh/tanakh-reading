<script lang="ts">
    import Icon from "./shared/Icon.svelte";

    export let starredCommentsCount: number;
    export let userCommentsCount: number;
</script>

{#if starredCommentsCount > 0 || userCommentsCount > 0}
    <span class="badge">
        {#if starredCommentsCount > 0}
            <span class="badge-item">
                <Icon icon="bookmark" color="var(--theme-color-bookmark-active)" heightEm={1} />
            </span>
        {/if}
        {#if userCommentsCount > 0}
            <span class="badge-item">
                <Icon icon="note-filled" color="var(--theme-color-user_comment-active)" heightEm={1} />
            </span>
        {/if}
    </span>
{/if}

<style>
    span.badge {
        font-size: xx-small;
        position: relative;
        top: -0.3em;
    }
</style>
