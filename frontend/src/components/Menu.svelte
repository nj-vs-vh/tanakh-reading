<script lang="ts">
    import { Link } from "svelte-routing";
    import BurgerMenu from "./shared/BurgerMenu/BurgerMenu.svelte";
    import MenuFolder from "./MenuItems/MenuFolder.svelte";
    import MenuFolderBlock from "./MenuItems/MenuFolderBlock.svelte";
    import TextSettings from "./MenuItems/TextSettings.svelte";
    import CommentsSettings from "./MenuItems/CommentsSettings.svelte";


    export let homeButton: boolean = false;

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
            <Link to="/">
                <MenuFolder icon="synagogue" title="Оглавление" />
            </Link>
        {/if}
        <TextSettings />
        <CommentsSettings />
        <MenuFolder icon="search" title="Поиск">
            <MenuFolderBlock title="Привет">
                <span>Ну привет</span>
            </MenuFolderBlock>
        </MenuFolder>
    </div>
</BurgerMenu>

<style>
    .inner-container {
        max-width: calc(90vw - 1.5em);
        padding-right: 1.5em;
    }
</style>
