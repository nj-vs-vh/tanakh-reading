<script lang="ts">
    import { getContext } from "svelte";

    import Menu from "../components/Menu.svelte";
    import BookParshaList from "../components/BookParshaList.svelte";

    import { setPageTitle } from "../utils";
    import type { Metadata } from "../types";

    setPageTitle(null);

    let metadata: Metadata = getContext("metadata");

    const bookIndices = Object.keys(metadata.book_names).map((v) => parseInt(v));
    bookIndices.sort();
</script>

<Menu />
<div class="horizontal-centering">
    <div class="vertical-flow-container">
        <h1>Тора</h1>
        <div class="cards-container">
            {#each bookIndices as bookIndex}
                <BookParshaList {bookIndex} />
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
