<script lang="ts">
    import MenuFolder from "./MenuFolder.svelte";
    import MenuFolderBlock from "./MenuFolderBlock.svelte";
    import { createEventDispatcher, getContext } from "svelte";
    import type { Metadata } from "../../types";
    import { textSourcesConfigStore } from "../../settings/textSources";
    import Keydown from "svelte-keydown";

    import {
        cmpVerseCoords,
        range,
        string2verseCoords,
        VerseCoords,
        versePath,
    } from "../../utils";
    import { navigateTo } from "svelte-router-spa";

    let mainTextSource: string;
    textSourcesConfigStore.subscribe((config) => {
        mainTextSource = config.main;
    });

    const metadata: Metadata = getContext("metadata");
    const latestParsha =
        metadata.available_parsha[metadata.available_parsha.length - 1];
    const availableBooks = Object.keys(metadata.book_names).filter(
        (book) => metadata.parsha_ranges[book][0] <= latestParsha
    );

    const dispatch = createEventDispatcher<{
        verseSearchResult: { parsha: number, chapter: number; verse: number };
    }>();

    let currentVerseCoordsInput: string = "";
    let currentBook: string = availableBooks[availableBooks.length - 1];
    let searchResultsNote = "";

    function findVerse() {
        const vc = string2verseCoords(currentVerseCoordsInput);
        if (vc !== null) {
            const parshasToSearch = range(
                metadata.parsha_ranges[currentBook][0],
                metadata.parsha_ranges[currentBook][1]
            );

            let parshaFound = false;
            for (const parsha of parshasToSearch) {
                const chapterVerseRange = metadata.chapter_verse_ranges[parsha];
                const vcStart: VerseCoords = {
                    chapter: chapterVerseRange[0][0],
                    verse: chapterVerseRange[0][1],
                };
                const vcEnd: VerseCoords = {
                    chapter: chapterVerseRange[1][0],
                    verse: chapterVerseRange[1][1],
                };
                if (
                    cmpVerseCoords(vc, vcStart) >= 0 && // both edges are inclusive
                    cmpVerseCoords(vcEnd, vc) >= 0 // both edges are inclusive
                ) {
                    parshaFound = true;
                    if (metadata.available_parsha.includes(parsha)) {
                        dispatch(
                            "verseSearchResult",
                            {parsha: parsha, chapter: vc.chapter, verse: vc.verse},
                        );
                        navigateTo(versePath(parsha, vc));
                    } else {
                        searchResultsNote =
                            "Недельный раздел со стихом ещё не доступен";
                    }
                }
            }
            if (!parshaFound) {
                searchResultsNote = "Стих не найден";
            }
        }
        currentVerseCoordsInput = "";
    }
</script>

<MenuFolder icon="search" title="Поиск">
    <MenuFolderBlock title="По стиху">
        <div class="search-bar-container">
            <select bind:value={currentBook}>
                {#each Object.entries(metadata.book_names) as [book, bookName]}
                    <option
                        value={book}
                        disabled={!availableBooks.includes(book)}
                        >{bookName[mainTextSource]}</option
                    >
                {/each}
            </select>
            <Keydown on:Enter={findVerse} />
            <input
                id="chapter-verse-input"
                type="text"
                placeholder="13:12"
                bind:value={currentVerseCoordsInput}
                on:input={() => {
                    searchResultsNote = "";
                }}
            />
            <button id="search-btn" on:click={findVerse}>Найти</button>
        </div>
        <div
            id="search-results-note"
            style={searchResultsNote === "" ? "display: none;" : ""}
        >
            {searchResultsNote}
        </div>
    </MenuFolderBlock>
</MenuFolder>

<style>
    div.search-bar-container {
        font-size: medium;
        display: flex;
        justify-content: space-between;
    }

    #chapter-verse-input {
        font-size: inherit;
        margin-right: 0.4em;
        max-width: 25%;
    }

    #search-btn {
        flex-grow: 4;
    }

    #search-results-note {
        padding: 0.2em;
        margin-top: 0.3em;
        text-align: center;
        color: rgb(126, 0, 0);
        font-size: medium;
    }

    select {
        flex-grow: 4;
        font-size: inherit;
        margin-right: 0.4em;
    }
</style>
