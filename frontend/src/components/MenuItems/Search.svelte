<script lang="ts">
    import { navigateTo } from "svelte-router-spa";
    import Keydown from "svelte-keydown";

    import MenuFolder from "./MenuFolder.svelte";
    import MenuFolderBlock from "./MenuFolderBlock.svelte";
    import { createEventDispatcher } from "svelte";
    import type { MultisectionMetadata } from "../../types";
    import { textSourcesConfigStore } from "../../settings/textSources";

    import { cmpVerseCoords, string2verseCoords, VerseCoords, versePath } from "../../utils";
    import SearchButton from "../shared/SearchButton.svelte";

    export let metadata: MultisectionMetadata;
    const availableBookIdsList = Object.values(metadata.sections)
        .flatMap((section) => section.parshas)
        .filter((parshaInfo) => metadata.available_parsha.includes(parshaInfo.id))
        .map((parshaInfo) => parshaInfo.book_id);
    const availableBookIds = [...new Set(availableBookIdsList)];
    availableBookIds.sort();

    const dispatch = createEventDispatcher<{
        verseSearchResult: { parsha: number; chapter: number; verse: number };
    }>();

    let currentVerseCoordsInput: string = "";
    let selectedBookId = availableBookIds[availableBookIds.length - 1];
    let searchResultsNote = "";

    function findVerse() {
        const vc = string2verseCoords(currentVerseCoordsInput);
        if (vc !== null) {
            const booksParshaInfoList = Object.values(metadata.sections)
                .flatMap((section) => section.parshas)
                .filter((pi) => pi.book_id === selectedBookId);
            let parshaFound = false;
            for (const parshaInfo of booksParshaInfoList) {
                const vcStart: VerseCoords = {
                    chapter: parshaInfo.chapter_verse_start[0],
                    verse: parshaInfo.chapter_verse_start[1],
                };
                const vcEnd: VerseCoords = {
                    chapter: parshaInfo.chapter_verse_end[0],
                    verse: parshaInfo.chapter_verse_end[1],
                };
                if (
                    cmpVerseCoords(vc, vcStart) >= 0 && // both edges are inclusive
                    cmpVerseCoords(vcEnd, vc) >= 0 // both edges are inclusive
                ) {
                    parshaFound = true;
                    if (metadata.available_parsha.includes(parshaInfo.id)) {
                        dispatch("verseSearchResult", { parsha: parshaInfo.id, chapter: vc.chapter, verse: vc.verse });
                        navigateTo(versePath(parshaInfo.id, vc));
                    } else {
                        searchResultsNote = "Недельный раздел не доступен";
                    }
                }
            }
            if (!parshaFound) {
                searchResultsNote = "Стих не найден";
            }
        }
        currentVerseCoordsInput = "";
    }

    let currentSearchQueryInput: string = "";
    function fullTextSearch() {
        navigateTo(`/search#${encodeURIComponent(currentSearchQueryInput)}`);
    }

    let bookInfoWithSectionKeys = Object.entries(metadata.sections).flatMap(([sectionKey, section]) =>
        section.books.map((bookInfo) => {
            return { sectionKey, bookInfo };
        }),
    );
</script>

<MenuFolder icon="search" title="Поиск">
    <MenuFolderBlock title="По стиху">
        <div class="search-bar-container">
            <select bind:value={selectedBookId}>
                {#each bookInfoWithSectionKeys as { sectionKey, bookInfo }}
                    <option value={bookInfo.id} disabled={!availableBookIds.includes(bookInfo.id)}
                        >{bookInfo.name[$textSourcesConfigStore[sectionKey].main]}</option
                    >
                {/each}
            </select>
            <!-- <Keydown on:Enter={findVerse} /> -->
            <input
                id="chapter-verse-input"
                type="text"
                placeholder="13:12"
                bind:value={currentVerseCoordsInput}
                on:input={() => {
                    searchResultsNote = "";
                }}
            />
            <SearchButton on:click={findVerse} />
        </div>
        <div id="search-results-note" style={searchResultsNote === "" ? "display: none;" : ""}>
            {searchResultsNote}
        </div>
    </MenuFolderBlock>
    <MenuFolderBlock title="По тексту">
        <div class="search-bar-container">
            <!-- <Keydown on:Enter={fullTextSearch} /> -->
            <input type="text" placeholder="" bind:value={currentSearchQueryInput} />
            <SearchButton on:click={fullTextSearch} />
        </div>
    </MenuFolderBlock>
</MenuFolder>

<style>
    div.search-bar-container {
        font-size: medium;
        display: flex;
        justify-content: space-between;
    }

    input {
        font-size: inherit;
        margin-right: 0.4em;
        flex-grow: 10;
        background-color: var(--theme-color-background);
    }

    select {
        background-color: var(--theme-color-background);
    }

    #chapter-verse-input {
        max-width: 25%;
    }

    #search-results-note {
        padding: 0.2em;
        margin-top: 0.3em;
        text-align: center;
        color: var(--theme-color-bad);
        font-size: medium;
    }

    select {
        flex-grow: 4;
        font-size: inherit;
        margin-right: 0.4em;
    }
</style>
