<script lang="ts">
    export let heightEm: number;
</script>

<div class="container" style="height: {heightEm}em">
    <slot />
</div>


<style>
    .container {
        width: auto;
        display: inline-flex;
        justify-content: center;
    }
</style>
