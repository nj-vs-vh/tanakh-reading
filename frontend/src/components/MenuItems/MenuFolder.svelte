<script lang="ts">
    import Icon from "../shared/Icon.svelte";

    export let icon: string;
    export let title: string;

    let isFolded = true;
    function toggleFolded() {
        isFolded = !isFolded;
    }
</script>

<h2 on:click={toggleFolded} on:keydown={toggleFolded}>
    <div class="nav-icon">
        <Icon heightEm={0.9} {icon} color="black" />
    </div>
    <span class="nav-caption">{title}</span>
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

    .nav-caption {
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
