<script lang="ts">
    import { getContext } from "svelte";
    import { Navigate } from "svelte-router-spa";

    import Screen from "../components/shared/Screen.svelte";

    import Menu from "../components/Menu.svelte";

    import { textSourcesConfigStore } from "../settings/textSources";
    import { parshaPath, range } from "../utils";
    import type { Metadata } from "../types";

    let metadata: Metadata = getContext("metadata");

    const bookIndices = Object.keys(metadata.book_names).map((v) => parseInt(v));
    bookIndices.sort();

    const parshaArrays = {};

    for (const [bookIndex, parshaMinMax] of Object.entries(metadata.parsha_ranges)) {
        parshaArrays[bookIndex] = range(parshaMinMax[0], parshaMinMax[1]);
    }
</script>

<Menu />
<Screen>
    <div class="container">
        <h1>Тора</h1>
        {#each bookIndices as bookIndex}
            <h2>
                {bookIndex}. {metadata.book_names[bookIndex][$textSourcesConfigStore.main]}
            </h2>
            {#each parshaArrays[bookIndex] as parshaIndex}
                {#if metadata.available_parsha.includes(parshaIndex)}
                    <Navigate to={parshaPath(parshaIndex)}>
                        <h3>
                            {parshaIndex}. {metadata.parsha_names[parshaIndex][$textSourcesConfigStore.main]}
                        </h3>
                    </Navigate>
                {:else}
                    <h3 class="inactive">
                        {parshaIndex}. {metadata.parsha_names[parshaIndex][$textSourcesConfigStore.main]}
                    </h3>
                {/if}
            {/each}
        {/each}
    </div>
</Screen>

<style>
    .container {
        min-width: 50vw;
        margin: 3em 1em;
    }

    h1 {
        margin: 3em 0 0 0;
    }

    h2 {
        margin: 1em 0 0 0;
    }

    h3 {
        margin: 0.5em 0 0 1em;
    }

    .inactive {
        color: rgb(196, 196, 196);
        cursor: not-allowed;
    }
</style>
