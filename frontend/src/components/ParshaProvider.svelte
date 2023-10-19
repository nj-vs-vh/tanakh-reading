<script lang="ts">
    import { getContext } from "svelte";
    import type { CurrentRoute } from "svelte-router-spa/types/components/route";

    import Parsha from "./Parsha.svelte";
    import Screen from "./shared/Screen.svelte";
    import Error from "./shared/Error.svelte";
    import Spinner from "./shared/Spinner.svelte";

    import type { Metadata, ParshaData } from "../types";
    import { getParsha } from "../api";

    const metadata: Metadata = getContext("metadata");

    export let currentRoute: CurrentRoute;

    let parshaPromise: Promise<ParshaData>;
    let lastLoadedParshaIndex: number | null = null;
    $: {
        let parshaIndex = parseInt(currentRoute.namedParams.parshaIndex);
        if (parshaIndex !== lastLoadedParshaIndex) {
            console.log(`Parsha provider: path change detected ${currentRoute.path}`);
            parshaPromise = getParsha(parshaIndex, metadata.logged_in_user !== null);
            lastLoadedParshaIndex = parshaIndex;
        }
    }
</script>

{#await parshaPromise}
    <Screen>
        <Spinner sizeEm={5} />
    </Screen>
{:then parshaData}
    <Parsha {parshaData} />
{:catch error}
    <Error {error} />
{/await}
