<script lang="ts">
    export let title: string | null = null;
</script>

<div class="block">
    {#if title !== null}
        <h4>{title}</h4>
    {/if}
    <slot />
</div>

<style>
    .block {
        margin-top: 0.7em;
        padding-left: var(--custom-border-spacing, 0.7em);
        margin-left: var(--custom-border-spacing, 0.7em);
        border-left: 2px var(--theme-color-secondary-border) solid;
        font-size: large;
    }
    h4 {
        margin: 0 0 0.2em 0;
    }
</style>
