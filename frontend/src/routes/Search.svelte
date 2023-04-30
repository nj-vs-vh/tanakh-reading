<script lang="ts">
    import Keydown from "svelte-keydown";
    import { inview } from "svelte-inview";

    import Menu from "../components/Menu.svelte";
    import SearchResultEntry from "../components/SearchResultEntry.svelte";
    import Hero from "../components/shared/Hero.svelte";
    import SearchButton from "../components/shared/SearchButton.svelte";
    import Spinner from "../components/shared/Spinner.svelte";
    import UpButton from "../components/shared/UpButton.svelte";

    import { searchText, SearchTextIn, SearchTextResponse, SearchTextSorting } from "../api";
    import { setPageTitle } from "../utils";

    let currentQuery = decodeURIComponent(window.location.hash.split("#").pop());

    let nextPageToFetch = 0;
    let pageSize = 30;
    let sorting = SearchTextSorting.START_TO_END;

    setPageTitle("Поиск");

    let sortingName = (s: SearchTextSorting) => {
        switch (s) {
            case SearchTextSorting.START_TO_END:
                return "от начала к концу";
            case SearchTextSorting.END_TO_START:
                return "от конца к началу";
            case SearchTextSorting.BEST_TO_WORST:
                return "по релевантности";
        }
    };

    // search settings
    let searchInTexts: boolean = true;
    let searchInComments: boolean = true;

    function atLeastOneSource(): boolean {
        return searchInTexts || searchInComments;
    }

    let currentSearchTextResponse: SearchTextResponse | null = null;
    let isLoading = false;
    let allLoaded = false;

    function resetSearch() {
        currentSearchTextResponse = null;
        nextPageToFetch = 0;
        isLoading = false;
        allLoaded = false;
    }

    let queryControlsEl: HTMLElement;

    async function loadSearchResponse() {
        window.location.hash = encodeURIComponent(currentQuery);
        isLoading = true;
        const searchIn = [];
        if (searchInComments) {
            searchIn.push(SearchTextIn.COMMENTS);
        }
        if (searchInTexts) {
            searchIn.push(SearchTextIn.TEXTS);
        }
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
        resetSearch();
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
<Hero verticalCentering={false}>
    <div id="query-controls" bind:this={queryControlsEl}>
        <div class="query-input-row">
            <input id="query-input" type="text" bind:value={currentQuery} />
            <SearchButton on:click={newSearch} />
            <Keydown on:Enter={newSearch} />
        </div>
        <div class="query-input-row secondary-query-controls">
            <span class="inline-controls-container">
                Искать в
                <input
                    id="search-in-texts-checkbox"
                    type="checkbox"
                    bind:checked={searchInTexts}
                    on:change={() => {
                        if (!atLeastOneSource()) {
                            searchInTexts = true;
                        } else {
                            newSearch();
                        }
                    }}
                />
                <label for="search-in-texts-checkbox">тексте</label>
                <input
                    id="search-in-comments-checkbox"
                    type="checkbox"
                    bind:checked={searchInComments}
                    on:change={() => {
                        if (!atLeastOneSource()) {
                            searchInComments = true;
                        } else {
                            newSearch();
                        }
                    }}
                />
                <label for="search-in-comments-checkbox">комментариях</label>
            </span>
        </div>
        <div class="query-input-row secondary-query-controls">
            <span class="inline-controls-container">
                Сортировка
                <select bind:value={sorting} on:change={newSearch}>
                    {#each Object.entries(SearchTextSorting) as [_, sts]}
                        <option value={sts}>{sortingName(sts)}</option>
                    {/each}
                </select>
            </span>
        </div>
    </div>
    {#if currentSearchTextResponse !== null}
        <p class="search-meta">
            <span>Всего совпадений:</span>
            {#if currentSearchTextResponse.total_matched_texts != null}
                <span
                    >{currentSearchTextResponse.total_matched_texts} в тексте{#if currentSearchTextResponse.total_matched_comments != null},
                    {/if}
                </span>
            {/if}
            {#if currentSearchTextResponse.total_matched_comments != null}
                <span>{currentSearchTextResponse.total_matched_comments} в комментариях </span>
            {/if}
        </p>
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
                if (inView) {
                    await loadMoreSearchResults();
                }
            }
        }}
    />
    {#if isLoading}
        <Spinner sizeEm={3} />
    {/if}
    {#if allLoaded}
        <UpButton
            on:up={() => {
                queryControlsEl.scrollIntoView();
            }}
        />
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

    div.query-input-row {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        margin-top: 0.5em;
    }

    div.secondary-query-controls {
        font-size: smaller;
        color: rgb(80, 80, 80);
    }

    span.inline-controls-container {
        display: flex;
        align-items: center;
    }

    span.inline-controls-container > input {
        margin: 0 0.5em;
    }

    span.inline-controls-container > select {
        margin: 0 0.5em;
        padding: 0.1em;
        background-color: unset;
    }

    div.search-entry-li-container {
        margin-top: 0.8em;
        padding-top: 0.4em;
        border-top: 1px grey solid;
    }

    p.search-meta {
        margin: 0;
        color: grey;
        font-size: small;
    }
</style>
