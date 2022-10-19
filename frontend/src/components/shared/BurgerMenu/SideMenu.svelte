<script lang="ts">
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
        <span>С Б-жьей помощью</span>
        <a
            href="https://github.com/nj-vs-vh/torah-reading/commmit/buildTimeReplacedVersion"
            target="_blank"
            rel="noreferrer"
            style="text-decoration: dashed">buildTimeReplacedVersion</a
        >
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

        overflow-y: auto;
    }

    #menu {
        text-align: left;
    }

    footer {
        color: rgb(94, 94, 94);
        padding: 1em;
        display: flex;
        justify-content: space-around;
    }
</style>
