<script lang="ts">
    import Keydown from "svelte-keydown";
    import Menu from "../components/Menu.svelte";
    import Hero from "../components/shared/Hero.svelte";
    import SearchButton from "../components/shared/SearchButton.svelte";

    let currentQuery = decodeURIComponent(window.location.hash.split("#").pop());

    async function search() {
        window.location.hash = encodeURIComponent(currentQuery);
        console.log(`current query: ${currentQuery}`);
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
</style>
