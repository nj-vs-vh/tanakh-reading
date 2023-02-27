<script lang="ts">
    import Icon from "./Icon.svelte";
</script>

<button on:click>
    <Icon icon="search" heightEm={1.2} />
</button>

<style>
    button {
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 4px;
    }
</style>
