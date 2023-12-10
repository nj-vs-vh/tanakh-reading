<script lang="ts">
    import { getContext } from "svelte";
    import { inview } from "svelte-inview";
    // @ts-expect-error
    import MultiSelect from "svelte-multiselect";

    import Menu from "../components/Menu.svelte";
    import SearchResultEntry from "../components/SearchResultEntry.svelte";
    import Hero from "../components/shared/Hero.svelte";
    import SearchButton from "../components/shared/SearchButton.svelte";
    import Spinner from "../components/shared/Spinner.svelte";
    import UpButton from "../components/shared/UpButton.svelte";
    import Screen from "../components/shared/Screen.svelte";

    import { getStarredCommentsMeta, lookupStarredComments } from "../api";
    import type { StarredCommentData } from "../api";
    import { setPageTitle } from "../utils";
    import type { SectionMetadata } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";

    const metadata: SectionMetadata = getContext("metadata");
    const textSourceMain = $textSourcesConfigStore.main; // this is not reactive, but so what
    const parshaIndex2OptionText = (parshaId: number) =>
        `${parshaId}. ${metadata.section.parshas.find((pi) => pi.id === parshaId).name[textSourceMain]}`;
    const optionText2ParshaIndex = (optionText: string) => parseInt(optionText.slice(0, optionText.indexOf(".")));

    const currentHash = decodeURIComponent(window.location.hash.split("#").pop());
    console.log(`Current hash value: ${currentHash}`);

    const preSelectedParshaIndices = currentHash
        .split(",")
        .map((pi) => parseInt(pi))
        .filter(Boolean);
    console.log(`Pre-selected parsa indices: ${preSelectedParshaIndices}`);
    let selectedParshaOptionTexts: string[] = preSelectedParshaIndices.map(parshaIndex2OptionText);

    let nextPageToFetch = 0;
    let pageSize = 30;

    setPageTitle("Мои закладки");

    const starredCommentsMetaPromise = getStarredCommentsMeta();

    let currentStarredCommentsData: Array<StarredCommentData> | null = null;
    let isLoading = false;
    let allLoaded = false;

    function resetSearch() {
        currentStarredCommentsData = null;
        nextPageToFetch = 0;
        isLoading = false;
        allLoaded = false;
    }

    let queryControlsEl: HTMLElement;

    async function loadNextPage(): Promise<StarredCommentData[]> {
        isLoading = true;
        const parshaIndices: number[] = selectedParshaOptionTexts.map(optionText2ParshaIndex);
        window.location.hash = parshaIndices.join(",");
        try {
            const res = await lookupStarredComments(parshaIndices, nextPageToFetch, pageSize);
            return res.starred_comments;
        } finally {
            isLoading = false;
        }
    }

    async function newSearch() {
        resetSearch();
        currentStarredCommentsData = await loadNextPage();
    }

    async function loadMoreSearchResults() {
        nextPageToFetch += 1;
        let nextPageStarredCommentsData = await loadNextPage();
        if (nextPageStarredCommentsData.length === 0) {
            allLoaded = true;
        } else {
            currentStarredCommentsData = [...currentStarredCommentsData, ...nextPageStarredCommentsData];
        }
    }

    // newSearch();
</script>

<Menu homeButton />
{#await starredCommentsMetaPromise}
    <Screen>
        <Spinner sizeEm={5} />
    </Screen>
{:then starredCommentsMeta}
    <Hero verticalCentering={false}>
        <div id="query-controls" bind:this={queryControlsEl}>
            <div class="query-input-row">
                <span>В недельных разделах:</span>
                <span id="query-input">
                    <MultiSelect
                        placeholder="любых"
                        options={Object.keys(starredCommentsMeta.total_by_parsha).map((parshaIndexStr) =>
                            parshaIndex2OptionText(parseInt(parshaIndexStr)),
                        )}
                        bind:selected={selectedParshaOptionTexts}
                    />
                </span>
                <SearchButton on:click={newSearch} />
            </div>
        </div>
        {#if currentStarredCommentsData !== null}
            {#if currentStarredCommentsData.length > 0}
                {#each currentStarredCommentsData as starredCommentData}
                    <div class="search-entry-li-container">
                        <SearchResultEntry
                            match={{
                                text: null,
                                comment: starredCommentData.comment,
                                parsha_data: starredCommentData.parsha_data,
                            }}
                            isCommentStarrable={true}
                            addTextCommentIcon={false}
                        />
                    </div>
                {/each}
            {:else}
                <p>Пока ничего...</p>
            {/if}
        {/if}
        <div
            use:inview={{}}
            on:enter={async (e) => {
                const { inView } = e.detail;
                if (currentStarredCommentsData !== null && !allLoaded) {
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
{/await}

<style>
    #query-controls {
        font-size: large;
        margin-top: 2em;
        margin-bottom: 1em;
    }

    #query-input {
        margin: 0 0.4em;
        flex-grow: 100;
        max-width: 60%;
        --sms-min-height: 100%;
        --sms-font-size: medium;
        --sms-text-color: var(--theme-color-secondary-text);
    }

    div.query-input-row {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-evenly;
        margin-top: 0.5em;
    }

    div.search-entry-li-container {
        margin-top: 0.8em;
        padding-top: 0.4em;
        border-top: 1px var(--theme-color-secondary-border) solid;
    }
</style>
