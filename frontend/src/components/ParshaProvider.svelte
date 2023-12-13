<script lang="ts">
    import { getContext, setContext } from "svelte";
    import type { CurrentRoute } from "svelte-router-spa/types/components/route";

    import Parsha from "./Parsha.svelte";
    import Screen from "./shared/Screen.svelte";
    import Error from "./shared/Error.svelte";
    import Spinner from "./shared/Spinner.svelte";

    import type { ParshaData, MultisectionMetadata } from "../types";
    import { getParsha } from "../api";
    import NotFound from "../routes/NotFound.svelte";

    const metadata: MultisectionMetadata = getContext("metadata");

    export let currentRoute: CurrentRoute;

    let loadParshaPromise: Promise<ParshaData | null>;

    async function loadParsha(parshaId: number): Promise<ParshaData | null> {
        try {
            return getParsha(parshaId, metadata.logged_in_user !== null);
        } catch (e) {
            // convert parsha not found error to null so that user is forwarded to 404 page
            const errorText: string = e;
            if (errorText.includes("404")) {
                return null;
            } else {
                throw e;
            }
        }
    }

    let lastLoadedParshaId: number | null = null;
    $: {
        let parshaIdOrUrlName = currentRoute.namedParams.parshaId;
        let parshaId: number | undefined = undefined;
        if (/^\d+$/.test(parshaIdOrUrlName)) {
            parshaId = parseInt(parshaIdOrUrlName);
        } else {
            const parshaInfo = Object.values(metadata.sections)
                .flatMap((section) => section.parshas)
                .find((parshaInfo) => parshaInfo.url_name === parshaIdOrUrlName);
            if (parshaInfo !== undefined) parshaId = parshaInfo.id;
        }

        if (parshaId === undefined) {
            loadParshaPromise = Promise.resolve(null);
        } else if (parshaId !== lastLoadedParshaId) {
            console.log(`Parsha provider: path change detected ${currentRoute.path}`);
            let sectionKey = Object.entries(metadata.sections).find(
                ([_sectionKey, section]) =>
                    section.parshas.find((parshaInfo) => parshaInfo.id === parshaId) !== undefined,
            )[0];
            console.log(`Inferred section key from parsha id = ${parshaId}: ${sectionKey}`);
            setContext("sectionKey", sectionKey);
            loadParshaPromise = loadParsha(parshaId);
            lastLoadedParshaId = parshaId;
        }
    }
</script>

{#await loadParshaPromise}
    <Screen>
        <Spinner sizeEm={5} />
    </Screen>
{:then parshaData}
    {#if parshaData !== null}
        <Parsha {parshaData} />
    {:else}
        <NotFound />
    {/if}
{:catch error}
    <Error {error} />
{/await}
