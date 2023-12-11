<script lang="ts">
    import type { SectionKey } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";
    import MenuFolder from "./MenuItems/MenuFolder.svelte";
    import { parshaPath } from "../utils";
    import { Navigate } from "svelte-router-spa";
    import type { ParshaInfo, TanakhBookInfo } from "../typesGenerated";

    export let sectionKey: SectionKey;
    export let bookInfo: TanakhBookInfo;
    export let sectionParshaInfos: ParshaInfo[];
    export let availableParshaId: number[];

    const bookParshaInfos = sectionParshaInfos.filter((p) => p.book_id === bookInfo.id).sort((p1, p2) => p1.id - p2.id);
    const minSectionParshaId: number = Math.min.apply(null, sectionParshaInfos.map(p => p.id));
    const parshaIndexInBook = (parshaId: number) => parshaId - minSectionParshaId + 1;
</script>

<div class="container">
    <MenuFolder title={bookInfo.name[$textSourcesConfigStore[sectionKey].main]}>
        <div>
            {#each bookParshaInfos as parshaInfo}
                {#if availableParshaId.includes(parshaInfo.id)}
                    <Navigate to={parshaPath(parshaInfo.id)}>
                        <h3>
                            {parshaIndexInBook(parshaInfo.id)}. {parshaInfo.name[$textSourcesConfigStore[sectionKey].main]}
                        </h3>
                    </Navigate>
                {:else}
                    <h3 class="not-uploaded-yet-parsha">
                        {parshaIndexInBook(parshaInfo.id)}. {parshaInfo.name[$textSourcesConfigStore[sectionKey].main]}
                    </h3>
                {/if}
            {/each}
        </div>
    </MenuFolder>
</div>

<style>
    .container {
        --custom-border-spacing: 0.5em;
        border: 1px var(--theme-color-border) solid;
        border-radius: 5px 0 0 5px;
        padding: 0 0.5em;
        align-self: start;
        /* width: max(90%, 300px); */
    }
    .not-uploaded-yet-parsha {
        color: var(--theme-color-secondary-text);
        cursor: not-allowed;
    }
</style>
