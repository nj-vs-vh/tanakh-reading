<script lang="ts">
    import type { CurrentRoute } from "svelte-router-spa/types/components/route";

    import Parsha from "./Parsha.svelte";
    import Screen from "./shared/Screen.svelte";
    import Error from "./shared/Error.svelte";
    import Spinner from "./shared/Spinner.svelte";

    import type { ParshaData } from "../types";
    import { getParsha } from "../api";

    export let currentRoute: CurrentRoute;

    let parshaPromise = new Promise<string | ParshaData>((resolve, reject) => {});
    let lastLoadedParshaIndex: number | null = null;
    $: {
        let parshaIndex = parseInt(currentRoute.namedParams.parshaIndex);
        if (parshaIndex != lastLoadedParshaIndex) {
            console.log(`Parsha provider: path change detected ${currentRoute.path}`);
            parshaPromise = getParsha(parshaIndex);
            lastLoadedParshaIndex = parshaIndex;
        }
    }
</script>

{#await parshaPromise}
    <Screen>
        <Spinner sizeEm={5} />
    </Screen>
{:then parsha}
    {#if typeof parsha === "string"}
        <Screen>
            <Error errorMessage={parsha} />
        </Screen>
    {:else}
        <Parsha {parsha} />
    {/if}
{:catch error}
    <Error errorMessage={error.message} />
{/await}
