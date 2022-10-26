<button style="color: grey;" on:click={() => window.history.go(-1)}>
    <svg width="32" height="32" viewBox="-4 -4 40 40">
        <line id="top" x1="0" y1="18.5" x2="14" y2="4" />
        <line id="mid" x1="0" y1="18.5" x2="32" y2="18.5" />
        <line id="bot" x1="0" y1="18.5" x2="14" y2="32" />
    </svg>
</button>

<style>
    button {
        position: fixed;
        left: 0px;
        top: 0px;

        margin: 7px;

        z-index: 10;

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
</style>
