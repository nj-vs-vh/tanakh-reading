<script lang="ts">
    import type { ParshaData } from "../types";
    import { TextSource } from "../types";

    export let parsha: ParshaData;

    function limitSelectableTextToOneVerse(event) {
        console.log("HELLOOOO");
    }

</script>

<div class="container">
    {#each parsha.chapters as chapter}
        <h2>Глава {chapter.chapter}</h2>
        {#each chapter.verses as verse}
            <span class="verse-number">{verse.verse}.</span>
            <span class="verse-text">{verse.text[TextSource.FG]}</span>
            <!-- <br/> -->
        {/each}
    {/each}
</div>

<style>
    div.container {
        text-align: justify;
    }

    span.verse-number {
        color: grey;
        margin-right: 0.5em;
        user-select: none;
    }

    span.verse-text {
        margin-right: 1em;
    }
</style>
