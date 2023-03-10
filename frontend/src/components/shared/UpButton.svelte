<script lang="ts">
    import { createEventDispatcher } from "svelte";
    const dispatch = createEventDispatcher();

    function clicked() {
        dispatch("up", {});
    }
</script>

<div class="wide-clickable" on:click={clicked} on:keydown={clicked}>
    <span>↑</span>
</div>

<style>
    div.wide-clickable {
        font-size: large;
        width: 100%;
        display: flex;
        justify-content: center;
        cursor: pointer;
    }
</style>
