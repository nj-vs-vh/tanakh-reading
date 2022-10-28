<script lang="ts">
    export let urls: string[];
</script>

{#each Array.from(urls.entries()) as [index, link]}
    <sup>
        <a href={link} target="_blank" rel="noreferrer" class="external-link">
            {index + 1}
        </a>
    </sup>
{/each}

<style>
    a.external-link {
        color: rgb(50, 50, 77);
        padding: 0 0.2em;
        text-decoration: underline;
    }

    a.external-link:hover {
        color: rgb(26, 26, 182);
    }
</style>
