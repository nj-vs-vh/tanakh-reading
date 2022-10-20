<script lang="ts">
    import type { Metadata } from "../types";
    import { setContext } from "svelte";
    import Modal from "svelte-simple-modal";
    import { Router } from "svelte-router-spa";

    import { initCommentSourceFlags } from "../settings/commentSources";
    import { initTextDecorationStyle } from "../settings/textDecorationStyle";
    import { initCommentStyle } from "../settings/commentStyle";
    import {
        initTextSourcesConfig,
        textSourcesConfigStore,
    } from "../settings/textSources";
    import { getUrlHashVerseCoords, range, setUrlHash } from "../utils";

    import { routes } from "../routes";

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

    const parshaArrays = {};

    for (const [bookIndex, parshaMinMax] of Object.entries(
        metadata.parsha_ranges
    )) {
        parshaArrays[bookIndex] = range(parshaMinMax[0], parshaMinMax[1]);
    }
</script>

<Modal styleCloseButton={{ boxShadow: "none" }} on:close={() => {getUrlHashVerseCoords() === null ? null : setUrlHash("")}}>
    <Router {routes} />
</Modal>
