<script lang="ts">
    import Icon from "./Icon.svelte";
</script>

<button on:click={() => window.history.go(-1)}>
    <Icon icon="back" color="grey" heightEm={2}/>
</button>

<style>
    button {
        position: absolute;
        left: 0px;
        top: 0px;

        margin: 9px;

        z-index: 10;

        background-color: Transparent;
        background-repeat: no-repeat;
        border: none;
        cursor: pointer;
        overflow: hidden;
        outline: none;
    }
</style>
