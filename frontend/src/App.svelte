<script lang="ts">
    import { ThemeWrapper } from "svelte-themer";

    import Screen from "./components/shared/Screen.svelte";
    import Error from "./components/shared/Error.svelte";
    import Spinner from "./components/shared/Spinner.svelte";
    import Main from "./components/Main.svelte";

    import { getMetadata } from "./api";
    import themes from "./themes";

    let metadataPromise = getMetadata();
</script>

<ThemeWrapper {themes}>
    {#await metadataPromise}
        <Screen>
            <Spinner sizeEm={5} />
        </Screen>
    {:then metadata}
        <Main {metadata} />
    {:catch error}
        <Error {error} />
    {/await}
</ThemeWrapper>

<style>
    :global(html) {
        background-color: var(--theme-color-background, initial);
        color: var(--theme-color-text, initial);
    }
</style>
