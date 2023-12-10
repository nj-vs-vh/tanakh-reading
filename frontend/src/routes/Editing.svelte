<script lang="ts">
    import { getContext } from "svelte";
    import type { SectionMetadata } from "../types";
    import Error from "../components/shared/Error.svelte";
    import EditTexts from "../components/Editing/EditTexts.svelte";

    const metadata: SectionMetadata = getContext("metadata");
</script>

{#if metadata.logged_in_user === null || !metadata.logged_in_user.is_editor}
    <Error error="Требуются права редактора" />
{:else}
    <EditTexts />
{/if}
