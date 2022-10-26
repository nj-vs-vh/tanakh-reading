<script lang="ts">
    import { Rainbow } from 'svelte-loading-spinners';

    export let sizeEm: number;
    export let marginTopPx: number = 30;

    let hue: number = 0;
    const hue2color = (hue: number) => `hsl(${hue}, 88%, 57%)`
    let color: string = hue2color(hue)
    setInterval(
        () => {
            hue += 5;
            color = hue2color(hue);
        },
        30,
    )

</script>

<div class="container" style="margin-top: {marginTopPx}px;">
    <Rainbow color={color} size={sizeEm} unit="rem" />
</div>

<style>
    .container {
        width: 100%;
        display: flex;
        align-content: center;
        justify-content: center;
    }
</style>
