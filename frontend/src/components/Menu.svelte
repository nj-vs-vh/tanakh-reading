<script lang="ts">
    import { Navigate } from "svelte-router-spa";
    import { getContext } from "svelte";

    import BurgerMenu from "./shared/BurgerMenu/BurgerMenu.svelte";
    import MenuFolder from "./MenuItems/MenuFolder.svelte";
    import TextSettings from "./MenuItems/TextSettings.svelte";
    import CommentsSettings from "./MenuItems/CommentsSettings.svelte";
    import Search from "./MenuItems/Search.svelte";
    import type { Metadata } from "../types";

    export let homeButton: boolean = false;

    const metadata: Metadata = getContext("metadata");

    const backgroundColor = "#dddddd";
</script>

<BurgerMenu
    duration={0.2}
    width="400px"
    {backgroundColor}
    burgerColor={backgroundColor}
    menuColor="black"
    padding="10px"
    paddingTop="60px"
>
    <div class="inner-container">
        {#if homeButton}
            <Navigate to="/">
                <MenuFolder icon="synagogue" title="Главная" />
            </Navigate>
        {/if}
        <TextSettings />
        <CommentsSettings />
        <Search on:verseSearchResult />
        {#if metadata.logged_in_user === null}
            <Navigate to="/login">
                <MenuFolder icon="user" title="Войти" />
            </Navigate>
        {:else}
            <Navigate to="/account">
                <MenuFolder icon="user" title="Аккаунт" />
            </Navigate>
        {/if}
    </div>
</BurgerMenu>

<style>
    .inner-container {
        max-width: calc(90vw - 1.5em);
        padding-right: 1.5em;
    }
</style>
