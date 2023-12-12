<script lang="ts">
    import { getContext, setContext } from "svelte";
    import type { CurrentRoute } from "svelte-router-spa/types/components/route";

    import Parsha from "./Parsha.svelte";
    import Screen from "./shared/Screen.svelte";
    import Error from "./shared/Error.svelte";
    import Spinner from "./shared/Spinner.svelte";

    import type { ParshaData, MultisectionMetadata } from "../types";
    import { getParsha } from "../api";

    const metadata: MultisectionMetadata = getContext("metadata");

    export let currentRoute: CurrentRoute;

    let parshaPromise: Promise<ParshaData>;
    let lastLoadedParshaId: number | null = null;
    $: {
        let parshaId = parseInt(currentRoute.namedParams.parshaId);
        if (parshaId !== lastLoadedParshaId) {
            console.log(`Parsha provider: path change detected ${currentRoute.path}`);
            let sectionKey = Object.entries(metadata.sections).find(
                ([_sectionKey, section]) =>
                    section.parshas.find((parshaInfo) => parshaInfo.id === parshaId) !== undefined,
            )[0];
            console.log(`Inferred section key from parsha id = ${parshaId}: ${sectionKey}`)
            setContext("sectionKey", sectionKey);
            parshaPromise = getParsha(parshaId, metadata.logged_in_user !== null);
            lastLoadedParshaId = parshaId;
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
