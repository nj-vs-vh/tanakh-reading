<script lang="ts">
    import { getContext } from "svelte";
    import type { Metadata } from "../types";
    import Error from "../components/shared/Error.svelte";
    import EditTexts from "../components/EditTexts.svelte";

    const metadata: Metadata = getContext("metadata");
</script>

{#if metadata.logged_in_user === null || !metadata.logged_in_user.is_editor}
    <Error error="Требуются права редактора" />
{:else}
    <EditTexts />
{/if}
