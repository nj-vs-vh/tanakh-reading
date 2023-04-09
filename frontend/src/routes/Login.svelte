<script lang="ts">
    import Keydown from "svelte-keydown";
    import { navigateTo } from "svelte-router-spa";
    import { login } from "../api";
    import { saveAccessToken } from "../auth";

    import Hero from "../components/shared/Hero.svelte";
    import { setPageTitle } from "../utils";

    let username = "";
    let password = "";

    let loginError: string | null = null;

    setPageTitle("Логин");

    async function onLogin() {
        if (username.length < 5 || password.length < 6) return;

        try {
            const accessToken = await login({ username, password });
            saveAccessToken(accessToken.token);
            navigateTo("/account");
            window.location.reload();
        } catch (e) {
            loginError = e;
        }
    }
</script>

<Hero>
    <input type="text" name="username" placeholder="Юзернейм" bind:value={username} />
    <input type="password" name="password" placeholder="Пароль" bind:value={password} />
    <button on:click={onLogin}>Войти</button>
    <Keydown on:Enter={onLogin} />
    <div hidden={loginError === null} class="error-badge">
        {loginError}
    </div>
</Hero>

<style>
    button {
        margin: 1em 0;
        padding: 0.5em;
    }

    input {
        margin: 0.5em 0;
    }
</style>
