<script lang="ts">
    import type { ParshaData } from "../types";
    import { TextSource } from "../types";

    export let parsha: ParshaData;
</script>

<div class="page">
    <div class="container">
        {#each parsha.chapters as chapter}
            <h2>Глава {chapter.chapter}</h2>
            {#each chapter.verses as verse}
                <span class="verse-number">{verse.verse}.</span>
                <span class="verse-text">{verse.text[TextSource.FG]}</span>
            {/each}
        {/each}
    </div>
</div>

<style>
    div.page {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1em 0 1em 0;
    }
    div.container {
        text-align: justify;
        width: max(50vw, 600px);
        /* font-size: large; */
    }

    span.verse-number {
        color: grey;
        margin-right: 0.3em;
        user-select: none;
    }

    span.verse-text {
        margin-right: 0.5em;
    }
</style>
