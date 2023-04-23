<script lang="ts">
    import Screen from "./Screen.svelte";

    export let verticalCentering: boolean = false;
</script>

<Screen {verticalCentering}>
    <div class="container">
        <slot />
    </div>
</Screen>

<style>
    div.container {
        width: max(30vw, 600px);
        max-width: 90vw;
        display: flex;
        flex-direction: column;
        padding: 1em;
    }
</style>
