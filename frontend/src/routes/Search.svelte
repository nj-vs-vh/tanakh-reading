<script lang="ts">
    import Keydown from "svelte-keydown";
    import { inview } from "svelte-inview";

    import { searchText, SearchTextIn, SearchTextResponse, SearchTextSorting } from "../api";
    import Menu from "../components/Menu.svelte";
    import SearchResultEntry from "../components/SearchResultEntry.svelte";
    import Hero from "../components/shared/Hero.svelte";
    import SearchButton from "../components/shared/SearchButton.svelte";
    import Spinner from "../components/shared/Spinner.svelte";
    import { sleep } from "../utils";

    let currentQuery = decodeURIComponent(window.location.hash.split("#").pop());

    let nextPageToFetch = 0;
    let pageSize = 5;
    let sorting = SearchTextSorting.START_TO_END;
    let searchIn = [SearchTextIn.COMMENTS, SearchTextIn.TEXTS];

    let currentSearchTextResponse: SearchTextResponse | null = null;
    let isLoading = false;
    let allLoaded = false;

    async function loadSearchResponse() {
        window.location.hash = encodeURIComponent(currentQuery);
        isLoading = true;
        // await sleep(1);
        try {
            return await searchText({
                query: currentQuery,
                page: nextPageToFetch,
                page_size: pageSize,
                sorting: sorting,
                search_in: searchIn,
                with_verse_parsha_data: true,
            });
        } finally {
            isLoading = false;
        }
    }

    async function newSearch() {
        currentSearchTextResponse = null;
        nextPageToFetch = 0;
        currentSearchTextResponse = await loadSearchResponse();
    }

    async function loadMoreSearchResults() {
        nextPageToFetch += 1;
        let newSearchTextResponse = await loadSearchResponse();
        if (newSearchTextResponse.found_matches.length === 0) {
            allLoaded = true;
        }
        currentSearchTextResponse = {
            found_matches: currentSearchTextResponse.found_matches.concat(newSearchTextResponse.found_matches),
            total_matched_comments: currentSearchTextResponse.total_matched_comments,
            total_matched_texts: currentSearchTextResponse.total_matched_texts,
        };
    }

    if (currentQuery.length > 0) {
        newSearch();
    }
</script>

<Menu homeButton />
<Hero>
    <div id="query-controls">
        <div id="query-input-row">
            <input id="query-input" type="text" bind:value={currentQuery} />
            <SearchButton on:click={newSearch} />
            <Keydown on:Enter={newSearch} />
        </div>
    </div>
    {#if currentSearchTextResponse !== null}
        {#each currentSearchTextResponse.found_matches as foundMatch}
            <div class="search-entry-li-container">
                <SearchResultEntry match={foundMatch} />
            </div>
        {/each}
    {/if}
    <div
        use:inview={{}}
        on:enter={async (e) => {
            const { inView } = e.detail;
            if (currentSearchTextResponse !== null && !allLoaded) {
                // i.e. if the initial load is completed
                if (inView) {
                    await loadMoreSearchResults();
                }
            }
        }}
    />
    {#if isLoading}
        <Spinner sizeEm={3} />
    {/if}
</Hero>

<style>
    #query-controls {
        font-size: large;
        margin-top: 2em;
        margin-bottom: 1em;
    }

    #query-input {
        margin-right: 0.4em;
        flex-grow: 100;
        line-height: 1.2em;
    }

    #query-input-row {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
    }

    div.search-entry-li-container {
        margin-top: 0.8em;
        padding-top: 0.4em;
        border-top: 1px grey solid;
    }

    div.search-entry-li-container:first-of-type {
        background-color: red;
    }
</style>
