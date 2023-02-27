<script lang="ts">
    import type { CurrentRoute } from "svelte-router-spa/types/components/route";
    import Menu from "../components/Menu.svelte";
    import Hero from "../components/shared/Hero.svelte";
    import SearchButton from "../components/shared/SearchButton.svelte";

    export let currentRoute: CurrentRoute;

    console.log("currentRoute", currentRoute);

    let currentQuery: string = "";
    const url = new URL(window.location.toString());
    const urlQuery = url.searchParams.get("query");
    if (urlQuery !== null) {
        currentQuery = urlQuery;
    }

    let isCentered: boolean = currentQuery.length === 0 ? true : false;

    async function search() {
        currentRoute.queryParams.query = currentQuery;
        // const newUrl = new URL(window.location.toString());
        // newUrl.searchParams.set("query", currentQuery);
        // window.location.search = newUrl.search.toString();
        console.log("search", currentQuery);
        isCentered = false;
    }
</script>

<Menu homeButton />
<Hero>
    <div style={isCentered ? "" : "margin-top: 5em;"}>
        <div id="query-input-row">
            <input id="query-input" type="text" bind:value={currentQuery} />
            <SearchButton on:click={search} />
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
