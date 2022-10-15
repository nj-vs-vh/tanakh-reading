<script lang="ts">
    import {getParsha} from "../api"
    import Screen from "./shared/Screen.svelte";
    import Error from "./shared/Error.svelte";
    import Parsha from "./Parsha.svelte";
    import Spinner from "./shared/Spinner.svelte";

    export let parshaIndex: number;

    let parshaPromise = getParsha(parshaIndex);

</script>

{#await parshaPromise}
    <Screen>
        <Spinner sizeEm={5} />
    </Screen>
{:then parsha}
    {#if typeof parsha === "string"}
        <Screen>
            <Error errorMessage={parsha} />
        </Screen>
    {:else}
        <Parsha parsha={parsha}/>
    {/if}
{:catch error}
    <Error errorMessage={error.message} />
{/await}
