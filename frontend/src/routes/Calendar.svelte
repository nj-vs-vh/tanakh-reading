<script>
    import Screen from "../components/shared/Screen.svelte";

    let currentDateTime = new Date();

    setInterval(() => {
        currentDateTime = new Date();
    }, 3 * 1000);
</script>

<Screen>
    <h1>{currentDateTime.toLocaleString()}</h1>
    <span>{currentDateTime.toUTCString()}</span>
    <div id="clock" />
</Screen>

<style>
    #clock {
        aspect-ratio: 1;
        width: min(80vh, 80vw, 700px);
        border-radius: 100%;
        border: 3em solid black;
    }
</style>
