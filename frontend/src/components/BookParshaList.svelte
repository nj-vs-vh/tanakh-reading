<script lang="ts">
    import { getContext } from "svelte";
    import type { SectionMetadata } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";
    import MenuFolder from "./MenuItems/MenuFolder.svelte";
    import { parshaPath} from "../utils";
    import { Navigate } from "svelte-router-spa";

    let metadata: SectionMetadata = getContext("metadata");

    export let bookId: number;
    const bookParshaInfos = metadata.section.parshas.filter((pi) => pi.book_id === bookId).sort((a, b) => a.id - b.id);
    const bookName = metadata.section.books.find(bookInfo => bookInfo.id === bookId).name;

</script>

<div class="container">
    <MenuFolder title={bookName[$textSourcesConfigStore.main]}>
        <div>
            {#each bookParshaInfos as parshaInfo}
                {#if metadata.available_parsha.includes(parshaInfo.id)}
                    <Navigate to={parshaPath(parshaInfo.id)}>
                        <h3>
                            {parshaInfo.id}. {parshaInfo.name[$textSourcesConfigStore.main]}
                        </h3>
                    </Navigate>
                {:else}
                    <h3 class="not-uploaded-yet-parsha">
                        {parshaInfo.id}. {parshaInfo.name[$textSourcesConfigStore.main]}
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
