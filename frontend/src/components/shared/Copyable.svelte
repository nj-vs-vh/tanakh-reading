<script lang="ts">
    import Icon from "./Icon.svelte";

    export let content: string;

    let isCopied = false;

    function copyContent() {
        isCopied = true;
        navigator.clipboard.writeText(content);
    }
</script>

<div class="container">
    <span class="content">{content}</span>
    <span style="margin-left: 0.5em; cursor: pointer;" on:click={copyContent} on:keydown={copyContent}>
        <Icon icon={isCopied ? "check" : "copy"} heightEm={0.8} />
    </span>
</div>

<style>
    div.container {
        padding: 0.3em;
        border: 2px grey solid;
        background-color: rgb(238, 238, 238);
        border-radius: 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 100%;
    }

    span.content {
        padding: 0 0.5em;
        font-family: monospace;
        overflow-wrap: anywhere;
        overflow: hidden;
        white-space: break-spaces;
    }
</style>
