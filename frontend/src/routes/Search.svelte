<script lang="ts">
    import Keydown from "svelte-keydown";
    import { searchText, SearchTextIn, SearchTextResponse, SearchTextSorting } from "../api";
    import Menu from "../components/Menu.svelte";
    import SearchResultEntry from "../components/SearchResultEntry.svelte";
    import Hero from "../components/shared/Hero.svelte";
    import SearchButton from "../components/shared/SearchButton.svelte";
    import Spinner from "../components/shared/Spinner.svelte";
    import { sleep } from "../utils";

    let currentQuery = decodeURIComponent(window.location.hash.split("#").pop());

    let nextPageToFetch = 0;
    let pageSize = 50;
    let sorting = SearchTextSorting.START_TO_END;
    let searchIn = [SearchTextIn.COMMENTS, SearchTextIn.TEXTS];

    let currentSearchTextResponse: SearchTextResponse | null = null;
    let isLoading = false;

    async function search() {
        window.location.hash = encodeURIComponent(currentQuery);
        isLoading = true;
        // await sleep(1);
        try {
            currentSearchTextResponse = await searchText({
                query: currentQuery,
                page: nextPageToFetch,
                page_size: pageSize,
                sorting: sorting,
                search_in: searchIn,
                with_verse_parsha_data: false,
            });
            // currentSearchTextResponse = {
            //     found_matches: currentSearchTextResponse.found_matches.concat(newSearchTextResponse.found_matches),
            //     total_matched_comments: currentSearchTextResponse.total_matched_comments,
            //     total_matched_texts: currentSearchTextResponse.total_matched_texts,
            // };
        } finally {
            isLoading = false;
        }
    }

    if (currentQuery.length > 0) {
        search();
    }
</script>

<Menu homeButton />
<Hero>
    <div>
        <div id="query-input-row">
            <input id="query-input" type="text" bind:value={currentQuery} />
            <SearchButton on:click={search} />
            <Keydown on:Enter={search} />
        </div>
    </div>
    {#if currentSearchTextResponse !== null}
        {#each currentSearchTextResponse.found_matches as foundMatch}
            <div class="search-entry-li-container">
                <SearchResultEntry match={foundMatch} />
            </div>
        {/each}
    {/if}
    {#if isLoading}
        <Spinner sizeEm={3} />
    {/if}
</Hero>

<style>
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
        margin-top: 0.25em;
        padding-top: 0.25em;
    }
</style>
