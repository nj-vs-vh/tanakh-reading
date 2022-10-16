<script lang="ts">
    import type { Metadata } from "../types";
    import { setContext } from "svelte";
    import { Router, Link, Route } from "svelte-routing";
    import ParshaProvider from "./ParshaProvider.svelte";
    import { TextSource } from "../types";
    import Screen from "./shared/Screen.svelte";
    import Modal from "svelte-simple-modal";
    import Menu from "./Menu.svelte";
    import { initCommentSourceFlags } from "../commentSources";
    import { isProduction } from "../config";

    export let metadata: Metadata;
    setContext("metadata", metadata);

    initCommentSourceFlags(metadata);

    const bookIndices = Object.keys(metadata.book_names).map((v) =>
        parseInt(v)
    );
    bookIndices.sort();
    console.log(bookIndices);

    const parshaArrays = {};

    const range = (start, end) => {
        const length = end - start;
        return Array.from({ length }, (_, i) => start + i);
    };

    for (const [bookIndex, parshaMinMax] of Object.entries(
        metadata.parsha_ranges
    )) {
        parshaArrays[bookIndex] = range(parshaMinMax[0], parshaMinMax[1]);
    }
</script>

<Modal styleCloseButton={{ boxShadow: "none" }}>
    <Menu />
    <Router>
        <Route path="/">
            {#if isProduction}
                <!-- rendering title screen only in prod because
                    dev environment poorly supports client-side routing -->
                <Screen>
                    <div class="container">
                        <h1>Тора</h1>
                        {#each bookIndices as bookIndex}
                            <h2>
                                {bookIndex}. {metadata.book_names[bookIndex][
                                    TextSource.FG
                                ]}
                            </h2>
                            {#each parshaArrays[bookIndex] as parshaIndex}
                                {#if metadata.available_parsha.includes(parshaIndex)}
                                    <Link to={`/${parshaIndex}`}>
                                        <h3>
                                            {parshaIndex}. {metadata
                                                .parsha_names[parshaIndex][
                                                TextSource.FG
                                            ]}
                                        </h3>
                                    </Link>
                                {:else}
                                    <h3 class="inactive">
                                        {parshaIndex}. {metadata.parsha_names[
                                            parshaIndex
                                        ][TextSource.FG]}
                                    </h3>
                                {/if}
                            {/each}
                        {/each}
                    </div>
                </Screen>
            {:else}
                <ParshaProvider parshaIndex={3} />
            {/if}
        </Route>
        {#each metadata.available_parsha as parshaIndex}
            <Route path={`/${parshaIndex}`}>
                <ParshaProvider {parshaIndex} />
            </Route>
        {/each}
    </Router>
</Modal>

<style>
    .container {
        min-width: 50vw;
        margin-top: 3em;
        margin-bottom: 3em;
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
