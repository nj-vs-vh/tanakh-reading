<script lang="ts">
    export let errorMessage: string;
</script>

<div>
    <span>{errorMessage}</span>
</div>

<style>
    div {
        padding: 10px 15px;
        margin: 5px 0;
        background-color: #fffaf9;
        border: 1.5px solid #ff6c89;
        border-radius: 5px;
    }
</style>
