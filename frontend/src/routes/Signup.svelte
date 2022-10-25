<script lang="ts">
    import type { CurrentRoute } from "svelte-router-spa/types/components/route";
    import { checkSignupToken, signup } from "../api";
    import Screen from "../components/shared/Screen.svelte";
    import Error from "../components/shared/Error.svelte";
    import Spinner from "../components/shared/Spinner.svelte";
    import { navigateTo } from "svelte-router-spa";
    import Keydown from "svelte-keydown";

    export let currentRoute: CurrentRoute;
    const signupToken: string = currentRoute.namedParams.token;
    const checkSignupTokenPromise = checkSignupToken(signupToken);

    let username: string = '';
    let password: string = '';
    let fullName: string = '';

    let signupError: string | null = null;

    const usernameRe = /^[a-z0-9_-]+$/i;

    async function onSignup() {
        if (username.length < 5) {
            signupError = "Юзернейм не может быть короче 5 символов"
            return;
        }
        if (password.length < 6) {
            signupError = "Пароль не может быть короче 6 символов"
            return;
        }
        if (fullName.length < 1) {
            signupError = "Имя не может быть пустым"
            return;
        }
        if (!usernameRe.test(username)) {
            signupError = "Юзернейм может содержать только латинские буквы, цифры, нижний пробел и дефис"
            return;
        }

        const res = await signup(signupToken, {
            credentials: { username, password },
            data: { full_name: fullName }
        })
        signupError = res
        if (res === null) navigateTo("/")  // TODO: login and navigate to user management
    }
</script>

{#await checkSignupTokenPromise}
    <Screen>
        <Spinner sizeEm={5} />
    </Screen>
{:then isSignupTokenValid}
    {#if isSignupTokenValid}
        <Screen>
            <div class="container">
                <input
                    type="text"
                    name="username"
                    placeholder="Юзернейм"
                    bind:value={username}
                />
                <input
                    type="text"
                    name="full-name"
                    placeholder="Имя"
                    bind:value={fullName}
                />
                <input
                    type="password"
                    name="password"
                    placeholder="Пароль"
                    bind:value={password}
                />
                <button on:click={onSignup}>
                    Зарегистрироваться
                </button>
                <Keydown on:Enter={onSignup}/>
                <div hidden={signupError === null} class="error-badge">
                    {signupError}
                </div>
            </div>
        </Screen>
    {:else}
        <Screen>
            <h2>Ссылка для регистрации недействительна</h2>
        </Screen>
    {/if}
{:catch error}
    <Error errorMessage={error.message} />
{/await}

<style>
    input, button {
        margin: 0.5em 0;
        padding: 0.4em;
    }

    div.container {
        width: max(40vw, 700px);
        display: flex;
        flex-direction: column;
    }
</style>
