<script lang="ts">
    import { Rainbow } from 'svelte-loading-spinners';

    export let sizeEm: number;

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

<div class="container">
    <Rainbow color={color} size={sizeEm} unit="rem" />
</div>

<style>
    .container {
        margin-top: 30px;
        width: 100%;
        display: flex;
        align-content: center;
        justify-content: center;
    }
</style>
