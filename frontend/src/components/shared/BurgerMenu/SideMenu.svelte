<script lang="ts">
    import { ThemeToggle } from "svelte-themer";

    export let open;

    export let duration;
    export let width;
    export let padding;
    export let paddingTop;
    export let backgroundColor;
    export let menuColor;
</script>

<div
    id="container"
    style="background-color: {backgroundColor}; color: {menuColor}; width: {width}; left: {open
        ? '0px'
        : '-' + width}; transition: left {duration}s ease-in-out"
>
    <div id="menu" style="padding: {padding}; padding-top: {paddingTop}">
        <slot />
    </div>
    <footer>
        <div class="footer-row">
            <ThemeToggle />
        </div>
        <div class="footer-row">
            <span>С Б-жьей помощью</span>
            <a
                href="https://github.com/nj-vs-vh/torah-reading/tree/buildTimeReplacedVersion"
                target="_blank"
                rel="noreferrer"
                style="text-decoration: dashed">buildTimeReplacedVersion</a
            >
        </div>
    </footer>
</div>

<style>
    #container {
        position: fixed;
        height: 100vh;
        top: 0px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        z-index: 10;
        overflow-y: auto;
    }

    #menu {
        text-align: left;
    }

    footer {
        color: var(--theme-color-secondary-text);
        padding: 1em;
        display: flex;
        flex-direction: column;
    }

    div.footer-row {
        width: 100%;
        margin-top: 1em;
        display: flex;
        justify-content: space-around;
        align-items: center;
    }
</style>
