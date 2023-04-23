<script lang="ts">
    export let verticalCentering: boolean = true;
</script>

<div class={verticalCentering ? "screen-size-container vertical-centering" : "screen-size-container"}>
    <slot />
</div>

<style>
    .screen-size-container {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .vertical-centering {
        justify-content: center;
    }
</style>
