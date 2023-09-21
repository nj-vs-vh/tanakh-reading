<script lang="ts">
    import { getContext } from "svelte";

    import Menu from "../components/Menu.svelte";
    import BookParshaList from "../components/BookParshaList.svelte";

    import { setPageTitle } from "../utils";
    import type { Metadata } from "../types";
    import { Navigate } from "svelte-router-spa";

    setPageTitle(null);

    let metadata: Metadata = getContext("metadata");

    const bookIndices = Object.keys(metadata.book_names).map((v) => parseInt(v));
    bookIndices.sort();
</script>

<Menu />
<div class="horizontal-centering">
    <div class="vertical-flow-container">
        <div class="section">
            <h1>Тора</h1>
            <div class="cards-container">
                {#each bookIndices as bookIndex}
                    <BookParshaList {bookIndex} />
                {/each}
            </div>
        </div>
        <div class="section">
            <h1>
                <a class="calendar-link" href="/calendar">Календарь</a>
            </h1>
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

    .section {
        margin-bottom: 3rem;
        padding-top: 2.7rem;
        border-top: 1px var(--theme-color-border) solid;
    }

    .section:first-of-type {
        border-top: none;
    }

    h1 {
        margin-bottom: 1em;
        margin-top: 0;
    }

    .cards-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1rem;
    }

    .calendar-link:hover {
        text-decoration: underline;
        text-decoration-color: var(--theme-color-secondary-text);
    }
</style>
