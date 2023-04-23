<script lang="ts">
    import { getContext } from "svelte";
    import type { Metadata } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";
    import MenuFolder from "./MenuItems/MenuFolder.svelte";
    import { parshaPath, range } from "../utils";
    import { Navigate } from "svelte-router-spa";

    let metadata: Metadata = getContext("metadata");
    const parshaArrays = {};

    for (const [bookIndex, parshaMinMax] of Object.entries(metadata.parsha_ranges)) {
        parshaArrays[bookIndex] = range(parshaMinMax[0], parshaMinMax[1]);
    }

    export let bookIndex: number;
</script>

<div class="container">
    <MenuFolder title={metadata.book_names[bookIndex][$textSourcesConfigStore.main]}>
        <div>
            {#each parshaArrays[bookIndex] as parshaIndex}
                {#if metadata.available_parsha.includes(parshaIndex)}
                    <Navigate to={parshaPath(parshaIndex)}>
                        <h3>
                            {parshaIndex}. {metadata.parsha_names[parshaIndex][$textSourcesConfigStore.main]}
                        </h3>
                    </Navigate>
                {:else}
                    <h3 class="not-uploaded-yet-parsha">
                        {parshaIndex}. {metadata.parsha_names[parshaIndex][$textSourcesConfigStore.main]}
                    </h3>
                {/if}
            {/each}
        </div>
    </MenuFolder>
</div>

<style>
    .container {
        --custom-border-spacing: 0.5em;
        border: 1px grey solid;
        padding: 0 0.5em;
        align-self: start;
        /* width: max(90%, 300px); */
    }
    .not-uploaded-yet-parsha {
        color: rgb(196, 196, 196);
        cursor: not-allowed;
    }
</style>
