<script lang="ts">
    import { getContext } from "svelte";
    import { navigateTo } from "svelte-router-spa";
    import { generateSignupToken, logout } from "../api";
    import Hero from "../components/shared/Hero.svelte";
    import MainMenuButton from "../components/shared/MainMenuButton.svelte";
    import Copyable from "../components/shared/Copyable.svelte";

    import { getMySignupToken } from "../api";
    import type { Metadata } from "../types";
    import Spinner from "../components/shared/Spinner.svelte";
    import { setPageTitle, signupPath } from "../utils";
    import { deleteAccessToken } from "../auth";

    const metadata: Metadata = getContext("metadata");

    if (metadata.logged_in_user === null) {
        navigateTo("/login");
    }

    setPageTitle("Аккаунт");

    let mySignupTokenPromise = getMySignupToken();

    async function onGenerateSignupToken() {
        const token = await generateSignupToken();
        console.log(token);
        mySignupTokenPromise = new Promise((resolve, reject) => resolve(token));
    }

    async function onLogout() {
        await logout();
        deleteAccessToken();
        navigateTo("/");
        window.location.reload();
    }
</script>

{#if metadata.logged_in_user !== null}
    <MainMenuButton />
    <Hero>
        <h2>
            <span>{metadata.logged_in_user.data.full_name}</span>
            <span class="username">@{metadata.logged_in_user.username}</span>
        </h2>
        <div class="account-settings-block">
            <p>
                <strong>Ссылка-приглашение</strong>
                <span>для регистрации новых пользователь:ниц</span>
            </p>
            <p style="width: 100%; justify-content: center; display: flex; margin-top: 0.8em;">
                {#await mySignupTokenPromise}
                    <Spinner sizeEm={2} marginTopPx={0} />
                {:then signupToken}
                    {#if signupToken === null}
                        <button on:click={onGenerateSignupToken}>Сгенерировать</button>
                    {:else}
                        <Copyable content={window.location.origin + signupPath(signupToken.token)} />
                    {/if}
                {/await}
            </p>
        </div>
        <div class="account-settings-block">
            <p>
                <button style="padding: 0.5em 3em; font-weight: 600;" on:click={onLogout}>Выйти</button>
            </p>
        </div>
    </Hero>
{/if}

<style>
    span.username {
        color: grey;
        margin-left: 0.3em;
        font-size: large;
    }

    h2 {
        margin: 0;
    }

    p {
        margin: 0.3em 0;
    }

    div.account-settings-block {
        padding: 0.5em;
        margin-top: 1em;
        border: 1px grey solid;
        border-radius: 4px;
    }
</style>
