<script>
    import Screen from "./Screen.svelte";

</script>

<Screen>
    <div class="container">
        <slot/>
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
