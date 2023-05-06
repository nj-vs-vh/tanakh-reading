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
        color: var(--theme-color-secondary-text);
        padding: 0 0.2em;
        text-decoration: underline;
    }
</style>
