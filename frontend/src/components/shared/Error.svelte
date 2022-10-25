<script lang="ts">
    import Screen from "./Screen.svelte";

    export let errorMessage: string;
</script>

<Screen>
    <div class="error-badge">
        <span>{errorMessage}</span>
    </div>
</Screen>
