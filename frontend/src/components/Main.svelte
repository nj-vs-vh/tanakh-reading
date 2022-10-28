<script lang="ts">
    import type { Metadata } from "../types";
    import { setContext } from "svelte";
    import Modal from "svelte-simple-modal";
    import { Router } from "svelte-router-spa";

    import { initCommentFilters } from "../settings/commentFilters";
    import { initTextDecorationStyle } from "../settings/textDecorationStyle";
    import { initCommentStyle } from "../settings/commentStyle";
    import { initTextSourcesConfig, textSourcesConfigStore } from "../settings/textSources";
    import { getUrlHashVerseCoords, range, setUrlHash } from "../utils";

    import { routes } from "../routes";
    import { deleteAccessToken } from "../auth";
    import { initTextDecorationSettings } from "../settings/textDecorationSettings";

    export let metadata: Metadata;
    setContext("metadata", metadata);

    console.log(metadata);

    initCommentFilters(metadata);
    initTextSourcesConfig(metadata);
    initTextDecorationStyle();
    initCommentStyle();
    initTextDecorationSettings();
    if (metadata.logged_in_user === null) {
        deleteAccessToken(); // removing possible residual access token
    }

    let mainTextSource: string;
    textSourcesConfigStore.subscribe((config) => {
        mainTextSource = config.main;
    });

    const bookIndices = Object.keys(metadata.book_names).map((v) => parseInt(v));
    bookIndices.sort();

    const parshaArrays = {};

    for (const [bookIndex, parshaMinMax] of Object.entries(metadata.parsha_ranges)) {
        parshaArrays[bookIndex] = range(parshaMinMax[0], parshaMinMax[1]);
    }
</script>

<Modal
    styleCloseButton={{ boxShadow: "none", top: "0.5rem", right: "0.8rem" }}
    styleContent={{ padding: "0", overflowX: "hidden" }}
    styleBg={{ justifyContent: "flex-start" }}
    styleWindow={{ margin: "auto auto" }}
    on:close={() => {
        getUrlHashVerseCoords() === null ? null : setUrlHash("");
    }}
>
    <Router {routes} />
</Modal>
