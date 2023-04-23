<script lang="ts">
    export let title: string | null = null;
</script>

<div class="settings-block">
    {#if title !== null}
        <h4>{title}</h4>
    {/if}
    <slot />
</div>

<style>
    .settings-block {
        margin-top: 1em;
        padding-left: var(--custom-border-spacing, 1em);
        margin-left: var(--custom-border-spacing, 1em);
        border-left: 1px black solid;
        font-size: large;
    }
    h4 {
        margin: 0 0 0.2em 0;
    }
</style>
