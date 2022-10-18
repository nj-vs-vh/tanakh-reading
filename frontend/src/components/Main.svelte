<script lang="ts">
    import type { Metadata } from "../types";
    import { setContext } from "svelte";
    import { Router, Link, Route } from "svelte-routing";
    import ParshaProvider from "./ParshaProvider.svelte";
    import Screen from "./shared/Screen.svelte";
    import Modal from "svelte-simple-modal";
    import Menu from "./Menu.svelte";
    import { initCommentSourceFlags } from "../settings/commentSources";
    import { initTextDecorationStyle } from "../settings/textDecorationStyle";
    import { initCommentStyle } from "../settings/commentStyle";
    import {
        initTextSourcesConfig,
        textSourcesConfigStore,
    } from "../settings/textSources";
    import { getUrlHashVerseCoords, setUrlHash } from "../utils";

    export let metadata: Metadata;
    setContext("metadata", metadata);

    console.log(metadata);

    initCommentSourceFlags(metadata);
    initTextSourcesConfig(metadata);
    initTextDecorationStyle();
    initCommentStyle();

    let mainTextSource: string;
    textSourcesConfigStore.subscribe((config) => {
        mainTextSource = config.main;
    });

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

<Modal styleCloseButton={{ boxShadow: "none" }} on:close={() => {getUrlHashVerseCoords() === null ? null : setUrlHash("")}}>
    <Router>
        <Route path="/">
            <Menu />
            <Screen>
                <div class="container">
                    <h1>Тора</h1>
                    {#each bookIndices as bookIndex}
                        <h2>
                            {bookIndex}. {metadata.book_names[bookIndex][
                                mainTextSource
                            ]}
                        </h2>
                        {#each parshaArrays[bookIndex] as parshaIndex}
                            {#if metadata.available_parsha.includes(parshaIndex)}
                                <Link to={`/parsha${parshaIndex}`}>
                                    <h3>
                                        {parshaIndex}. {metadata.parsha_names[
                                            parshaIndex
                                        ][mainTextSource]}
                                    </h3>
                                </Link>
                            {:else}
                                <h3 class="inactive">
                                    {parshaIndex}. {metadata.parsha_names[
                                        parshaIndex
                                    ][mainTextSource]}
                                </h3>
                            {/if}
                        {/each}
                    {/each}
                </div>
            </Screen>
        </Route>
        {#each metadata.available_parsha as parshaIndex}
            <Route path={`/parsha${parshaIndex}`}>
                <ParshaProvider {parshaIndex} />
            </Route>
        {/each}
        <Route path={`*`}>
            <Screen>
                <h3 style="max-width: max(700px, 50vw); display: flex;">
                    <span style="color: grey; margin-right: 1em; white-space: nowrap;">Шемот 40:4</span>
                    <span>
                        И принеси (туда) стол, и расставь на нем посуду, и принеси светильник, и установи на нем лампы.
                    </span>
                </h3>
            </Screen>
        </Route>
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
