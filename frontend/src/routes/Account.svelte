<script lang="ts">
    import { getContext } from "svelte";
    import { navigateTo } from "svelte-router-spa";
    import { logout } from "../api";
    import Hero from "../components/shared/Hero.svelte";
    import ToMainMenu from "../components/shared/ToMainMenu.svelte";

    import type { Metadata } from "../types";

    const metadata: Metadata = getContext("metadata");

    if (metadata.logged_in_user === null) {
        navigateTo("/login")
    }

    async function onLogout() {
        await logout();
        navigateTo("/");
        window.location.reload();
    }
</script>

<ToMainMenu />
<Hero>
    <h2>
        <span>{metadata.logged_in_user.data.full_name}</span>
        <span class="username">@{metadata.logged_in_user.username}</span>
    </h2>
    <!-- <p>
        Ссылка-приглашение: {window.location.origin}
    </p> -->
    <p>
        <button on:click={onLogout}>Выйти</button>
    </p>
</Hero>

<style>
    span.username {
        color: grey;
        margin-left: 0.3em;
        font-size: large;
    }

    button {
        padding: 0.5em;
    }

</style>
