<script lang="ts">
    import { Link } from "svelte-routing";
    import Icon from "./shared/Icon.svelte";
    import InlineIcon from "./shared/InlineIcon.svelte";
    import BurgerMenu from "./shared/BurgerMenu/BurgerMenu.svelte";

    export let homeButton: boolean = false;

    const backgroundColor = "#cccccc";
</script>

<BurgerMenu
    duration={0.2}
    width="300px"
    {backgroundColor}
    burgerColor={backgroundColor}
    menuColor="black"
    padding="12px"
    paddingTop="60px"
>
    <div class="inner-container">
        {#if homeButton}
            <Link to="/">
                <h2>
                    <InlineIcon heightEm={1}>
                        <Icon icon="synagogue" color="black" />
                    </InlineIcon>
                    <span class="nav-caption">Оглавление</span>
                </h2>
            </Link>
        {/if}
        {#each [1, 1, 2, 3, 4, 5, 56, 6, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8] as index}
            <h2>Example</h2>
        {/each}
    </div>
</BurgerMenu>

<style>
    .inner-container {
        max-width: calc(90vw - 1.5em);
        padding-right: 1.5em;
    }

    h2 {
        margin: 0.4em 0 0.4em 0;
    }

    .nav-caption {
        margin-left: 0.3em;
    }
</style>
