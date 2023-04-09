<script lang="ts">
    import type { CurrentRoute } from "svelte-router-spa/types/components/route";
    import { checkSignupToken, login, signup } from "../api";
    import Screen from "../components/shared/Screen.svelte";
    import Error from "../components/shared/Error.svelte";
    import Spinner from "../components/shared/Spinner.svelte";
    import { navigateTo } from "svelte-router-spa";
    import Keydown from "svelte-keydown";
    import Hero from "../components/shared/Hero.svelte";
    import type { UserCredentials } from "../types";
    import { saveAccessToken } from "../auth";
    import { setPageTitle } from "../utils";

    setPageTitle("Регистрация");

    export let currentRoute: CurrentRoute;
    const signupToken: string = currentRoute.namedParams.token;
    const checkSignupTokenPromise = checkSignupToken(signupToken);

    let username: string = "";
    let password: string = "";
    let fullName: string = "";

    let signupError: string | null = null;

    const usernameRe = /^[a-z0-9_-]+$/i;

    async function onSignup() {
        if (username.length < 5) {
            signupError = "Юзернейм не может быть короче 5 символов";
            return;
        }
        if (password.length < 6) {
            signupError = "Пароль не может быть короче 6 символов";
            return;
        }
        if (fullName.length < 1) {
            signupError = "Имя не может быть пустым";
            return;
        }
        if (!usernameRe.test(username)) {
            signupError = "Юзернейм может содержать только латинские буквы, цифры, нижний пробел и дефис";
            return;
        }

        const credentials: UserCredentials = { username, password };

        const res = await signup(signupToken, {
            credentials: credentials,
            data: { full_name: fullName },
        });
        signupError = res;
        if (res === null) {
            try {
                const accessToken = await login(credentials);
                saveAccessToken(accessToken.token);
                navigateTo("/account");
                window.location.reload();
            } catch (e) {
                signupError = e;
            }
        }
    }
</script>

{#await checkSignupTokenPromise}
    <Screen>
        <Spinner sizeEm={5} />
    </Screen>
{:then isSignupTokenValid}
    {#if isSignupTokenValid}
        <Hero>
            <input type="text" name="username" placeholder="Юзернейм" bind:value={username} />
            <input type="password" name="password" placeholder="Пароль" bind:value={password} />
            <input type="text" name="full-name" placeholder="Имя" bind:value={fullName} />
            <button on:click={onSignup}>Создать учётную запись</button>
            <Keydown on:Enter={onSignup} />
            <div hidden={signupError === null} class="error-badge">
                {signupError}
            </div>
        </Hero>
    {:else}
        <Screen>
            <h2>Ссылка для регистрации недействительна</h2>
        </Screen>
    {/if}
{:catch error}
    <Error {error} />
{/await}

<style>
    button {
        margin: 1em 0;
        padding: 0.5em;
    }

    input {
        margin: 0.5em 0;
    }
</style>
