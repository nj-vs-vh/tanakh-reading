<script lang="ts">
    export let title: string;
</script>

<div class="settings-block">
    <h4>{title}</h4>
    <slot />
</div>

<style>
    .settings-block {
        margin-top: 1em;
        padding-left: 1em;
        margin-left: 1em;
        border-left: 1px black solid;
        font-size: large;
    }
    h4 {
        margin: 0 0 0.2em 0;
    }
</style>
