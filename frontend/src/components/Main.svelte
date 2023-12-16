<script lang="ts">
    import Keydown from "svelte-keydown";
    import type { MultisectionMetadata } from "../types";
    import { setContext } from "svelte";
    import Modal from "svelte-simple-modal";
    import { Router } from "svelte-router-spa";

    import { initCommentSourcesConfig } from "../settings/commentSources";
    import { initTextDecorationStyle } from "../settings/textDecorationStyle";
    import { initCommentStyle } from "../settings/commentStyle";
    import { initTextSourcesConfig } from "../settings/textSources";
    import { getUrlHashVerseCoords, setUrlHash } from "../utils";

    import { routes } from "../routes";
    import { deleteAccessToken } from "../auth";
    import { initTextDecorationSettings } from "../settings/textDecorationSettings";
    import { isEditingStore } from "../editing";

    export let metadata: MultisectionMetadata;
    setContext("metadata", metadata);

    console.log(metadata);

    initCommentSourcesConfig(metadata);
    initTextSourcesConfig(metadata);
    initTextDecorationStyle();
    initCommentStyle();
    initTextDecorationSettings();
    if (metadata.logged_in_user === null) {
        deleteAccessToken(); // removing possible residual access token
    }
</script>

<Modal
    styleCloseButton={{ boxShadow: "none", top: "0.5rem", right: "0.8rem", cursor: "pointer" }}
    styleContent={{
        padding: "0",
        overflowX: "hidden",
        color: "var(--theme-color-text)",
        backgroundColor: "var(--theme-color-background)",
    }}
    styleBg={{ justifyContent: "flex-start" }}
    styleWindow={{ margin: "auto auto" }}
    on:close={() => {
        getUrlHashVerseCoords() === null ? null : setUrlHash("");
        isEditingStore.set(false);
    }}
>
    <Keydown
        on:combo={(e) => {
            if (
                metadata.logged_in_user !== null &&
                metadata.logged_in_user.is_editor &&
                e.detail.endsWith("Control-q")
            ) {
                isEditingStore.set(true);
            }
        }}
    />
    <Router {routes} />
</Modal>
