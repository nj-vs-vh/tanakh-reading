<script lang="ts">
    import Icon from "./Icon.svelte";

    export let content: string;
</script>

<div class="container">
    <span
        style="overflow-wrap: anywhere; overflow: hidden; white-space: break-spaces;"
        >{content}</span
    >
    <span style="margin-left: 0.3em;">
        <Icon icon="copy" heightEm={0.8} />
    </span>
</div>

<style>
    div.container {
        padding: 0.3em;
        border: 1px grey solid;
        border-radius: 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 100%;
    }
</style>
