<!-- copied from https://github.com/jorisBarkema/svelte-burger-menu/blob/fa88b5631717753adc43e25827ca7edaa97493e8/src/BurgerButton.svelte -->
<script lang="ts">
    export let open;

    export let duration;
    export let burgerColor;
    export let menuColor;
</script>

<button
    class:open
    on:click={() => (open = !open)}
    style="transition: color {duration}s ease-in-out; color: {open
        ? menuColor
        : 'grey'}; background-image: radial-gradient({open ? burgerColor : 'transparent'}, transparent);"
>
    <svg width="32" height="32" viewBox="-4 -4 40 40">
        <line
            id="top"
            x1="0"
            y1="9"
            x2="32"
            y2="9"
            style="transition: transform {duration}s ease-in-out, opacity {duration}s ease-in-out;"
        />
        <line
            id="mid"
            x1="0"
            y1="18.5"
            x2="32"
            y2="18.5"
            style="transition: transform {duration}s ease-in-out, opacity {duration}s ease-in-out;"
        />
        <line
            id="bot"
            x1="0"
            y1="28"
            x2="32"
            y2="28"
            style="transition: transform {duration}s ease-in-out, opacity {duration}s ease-in-out;"
        />
    </svg>
</button>

<style>
    button {
        position: fixed;
        left: 0px;
        top: 0px;

        margin: 7px;

        z-index: 20;

        background-color: Transparent;
        background-repeat: no-repeat;
        border: none;
        cursor: pointer;
        overflow: hidden;
        outline: none;
    }

    svg line {
        stroke: currentColor;
        stroke-width: 3;
    }

    /* rotate the top line */
    button.open #top {
        transform: translate(10px, 0px) rotate(45deg);
    }

    /* hide the middle */
    button.open #mid {
        opacity: 0;
    }

    /* rotate the bottom line */
    button.open #bot {
        transform: translate(-15px, 8px) rotate(-45deg);
    }
</style>
