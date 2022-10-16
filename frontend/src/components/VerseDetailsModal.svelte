<script lang="ts">
    import { TextSource, VerseData } from "../types";
    import { commentSourceFlagsStore } from "../settings/commentSources";
    import type { CommentSourceFlags } from "../settings/commentSources";

    import VerseComments from "./VerseComments.svelte"

    let commentSourceFlags: CommentSourceFlags;
    commentSourceFlagsStore.subscribe((v) => {
        commentSourceFlags = v;
    });

    export let verseData: VerseData;
    export let chapter: number;
</script>

<div class="container">
    <p class="verse-number">{chapter}:{verseData.verse}</p>
    <blockquote>
        {verseData.text[TextSource.FG]}
    </blockquote>
    <VerseComments {verseData}/>
</div>

<style>
    .container {
        max-width: 60vw;
        margin: 0.3em 3em 0.3em 0.3em;
    }

    p {
        margin: 0.2em 0 0.1em 0;
    }

    p.verse-number {
        color: grey;
    }

    blockquote {
        margin: 0.3em 0.5em 0.9em 0.1em;
        padding: 0.1em 0.1em 0.1em 0.5em;
        border-left: solid rgb(179, 179, 179) 2px;
        color: rgb(68, 68, 68);
    }
</style>
