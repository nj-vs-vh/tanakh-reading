<script lang="ts">
    import { getContext } from "svelte";
    import { navigateTo } from "svelte-router-spa";
    import { generateSignupToken, getStarredCommentsMeta, logout } from "../api";

    import Menu from "../components/Menu.svelte";
    import Hero from "../components/shared/Hero.svelte";
    import Copyable from "../components/shared/Copyable.svelte";
    import SearchResultEntry from "../components/SearchResultEntry.svelte";
    import Icon from "../components/shared/Icon.svelte";
    import Spinner from "../components/shared/Spinner.svelte";

    import { getMySignupToken } from "../api";
    import type { Metadata } from "../types";
    import { setPageTitle, signupPath } from "../utils";
    import { deleteAccessToken } from "../auth";

    const metadata: Metadata = getContext("metadata");

    if (metadata.logged_in_user === null) {
        navigateTo("/login");
    }

    setPageTitle("Аккаунт");

    let mySignupTokenPromise = getMySignupToken();

    let starredCommentsMetaPromise = getStarredCommentsMeta();

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
    <Menu homeButton />
    <Hero verticalCentering={false}>
        <h1>
            <span>{metadata.logged_in_user.data.full_name}</span>
            <span class="username">@{metadata.logged_in_user.username}</span>
        </h1>
        <div class="account-settings-block">
            <h3>
                <Icon icon="bookmark" heightEm={0.75} />
                <span class="subtitle-with-icon">Мои закладки</span>
            </h3>
            {#await starredCommentsMetaPromise}
                <Spinner sizeEm={3} marginTopPx={0} />
            {:then starredCommentsMeta}
                {#if starredCommentsMeta.total === 0}
                    Пока ни одной...
                {:else}
                    <p>
                        Всего комментариев: <strong>{starredCommentsMeta.total}</strong>, например:
                    </p>
                    {#if starredCommentsMeta.random_starred_comment_data !== null}
                        <div class="random-starred-comment-container">
                            <SearchResultEntry
                                match={{
                                    text: null,
                                    comment: starredCommentsMeta.random_starred_comment_data.comment,
                                    parsha_data: starredCommentsMeta.random_starred_comment_data.parsha_data,
                                }}
                                isCommentStarrable={false}
                                addTextCommentIcon={false}
                            />
                        </div>
                    {/if}
                {/if}
            {/await}
        </div>
        <div class="account-settings-block">
            <h3>
                <Icon icon="user-plus" heightEm={1} />
                <span class="subtitle-with-icon">Ссылка-приглашение</span>
            </h3>
            {#await mySignupTokenPromise}
                <Spinner sizeEm={3} marginTopPx={0} />
            {:then signupToken}
                {#if signupToken === null}
                    <button on:click={onGenerateSignupToken}>Сгенерировать</button>
                {:else}
                    <Copyable content={window.location.origin + signupPath(signupToken.token)} />
                {/if}
            {/await}
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

    h1 {
        margin: 0;
        margin-top: min(max(1em, 10vw), 20vh);
        margin-bottom: 0.5em;
        padding-bottom: 0.5em;
        border-bottom: 1px grey solid;
    }

    h3 {
        margin: 0.1em 0 0.3em 0;
        display: inline-flex;
        align-items: center;
    }

    span.subtitle-with-icon {
        margin-left: 0.5em;
    }

    p {
        margin: 0.3em 0;
    }

    div.account-settings-block {
        margin-bottom: 1em;
        padding-bottom: 1em;
        border-bottom: 1px grey solid;
        display: flex;
        flex-direction: column;
    }

    div.random-starred-comment-container {
        background-color: rgb(238, 238, 238);
        padding: 0.5em;
        padding-top: 0.3em;
        border: 1px solid grey;
    }
</style>
