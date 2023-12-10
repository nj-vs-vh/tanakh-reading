<script lang="ts">
    import { getContext } from "svelte";

    import Menu from "../components/Menu.svelte";
    import BookParshaList from "../components/BookParshaList.svelte";

    import { setPageTitle } from "../utils";
    import type { SectionMetadata } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";

    setPageTitle(null);

    let metadata: SectionMetadata = getContext("metadata");

    const bookIndices = metadata.section.books.map(bi => bi.id).sort();
</script>

<Menu />
<div class="horizontal-centering">
    <div class="vertical-flow-container">
        <h1>{metadata.section.title[$textSourcesConfigStore.main]}</h1>
        {#if metadata.section.subtitle}
            <p>{metadata.section.subtitle[$textSourcesConfigStore.main]}</p>
        {/if}
        <div class="cards-container">
            {#each bookIndices as bookId}
                <BookParshaList {bookId} />
            {/each}
        </div>
    </div>
</div>

<style>
    .horizontal-centering {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .vertical-flow-container {
        min-width: 40vw;
        max-width: 100%;
        margin-top: 4em;
    }

    h1 {
        margin-bottom: 1em;
    }

    .cards-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1rem;
    }
</style>
