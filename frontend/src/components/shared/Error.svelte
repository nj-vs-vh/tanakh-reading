<script lang="ts">
    import Screen from "./Screen.svelte";

    export let error: string | Error;

    let errorMessage: string;

    if (typeof error === "object"){
        console.log(error);
        errorMessage = error.message;
    } else {
        errorMessage = error;
    }
</script>

<Screen>
    <div class="error-badge">
        <span>{errorMessage}</span>
    </div>
</Screen>
