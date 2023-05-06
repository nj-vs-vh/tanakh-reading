<script lang="ts">
    import Icon from "../shared/Icon.svelte";

    export let icon: string | null = null;
    export let title: string;
    export let iconSizeEm: number = 0.9;

    let isFolded = true;
    function toggleFolded() {
        isFolded = !isFolded;
    }
</script>

<h2 on:click={toggleFolded} on:keydown={toggleFolded}>
    {#if icon !== null}
        <div class="nav-icon">
            <Icon heightEm={iconSizeEm} {icon} color="var(--theme-color-text)" />
        </div>
    {/if}
    <span class={icon !== null ? "nav-caption-with-icon" : ""}>{title}</span>
</h2>
<div class={isFolded ? "folded" : ""}>
    <slot />
</div>

<style>
    h2 {
        margin: 0.4em 0;
        display: flex;
        flex-direction: row;
        align-items: center;
        cursor: pointer;
    }

    h2:hover {
        text-decoration: underline;
    }

    .nav-caption-with-icon {
        margin-left: 0.3em;
    }

    .nav-icon {
        display: flex;
        justify-content: center;
        align-items: center;
        min-width: 1.5em;
    }

    .folded {
        display: none;
        height: 0;
    }
</style>
