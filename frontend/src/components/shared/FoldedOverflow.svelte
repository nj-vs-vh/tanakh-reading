<script lang="ts">
    import { afterUpdate } from "svelte";

    export let maxHeightPx: number = 400;

    // HACK: used to force rerender of folded overflow component
    export let id: string = "";

    let isOverflown: boolean = false;
    let hasClickedReadMore: boolean = false;

    let overflowContainerEl: HTMLDivElement;
    afterUpdate(() => {
        // this is fucked up :0
        const isOverflownNew = overflowContainerEl.scrollHeight > maxHeightPx;
        console.debug(
            `afterUpdate id=${id} isOverflown ${isOverflown} -> ${isOverflownNew} hasClieckedReadMore=${hasClickedReadMore}`,
        );
        if (!isOverflownNew && isOverflown) {
            // this is executed when the content of <slot/> is updated
            // and the new content is actually not overflown
            console.debug("- setting isOverflown to false");
            isOverflown = false;
        }
        if (!hasClickedReadMore && isOverflownNew) {
            console.debug("+ setting isOverflown to true");
            isOverflown = true;
        }
        // after this callback, we reset has clicked flag so that it does not bleed to the next update
        hasClickedReadMore = false;
    });
</script>

<div
    style={isOverflown ? `max-height: ${maxHeightPx}px` : ""}
    class="overflow-container"
    bind:this={overflowContainerEl}
>
    <slot />
    {#if isOverflown}
        <button
            class="show-more"
            on:click={() => {
                isOverflown = false;
                hasClickedReadMore = true;
            }}>...</button
        >
    {/if}
</div>

<style>
    div.overflow-container {
        overflow-y: hidden;
    }

    button.show-more {
        position: absolute;
        left: 0;
        bottom: 0;
        width: 100%;
        height: 2em;
        font-weight: 800;
        font-size: larger;
        border: none;
        cursor: pointer;
        background: linear-gradient(0deg, white, transparent);
    }
</style>
