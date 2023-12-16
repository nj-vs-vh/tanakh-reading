<script lang="ts">
    import { getContext } from "svelte";

    import Menu from "../components/Menu.svelte";
    import TanakhBookCard from "../components/TanakhBookCard.svelte";

    import { setPageTitle } from "../utils";
    import type { MultisectionMetadata } from "../types";
    import { textSourcesConfigStore } from "../settings/textSources";

    setPageTitle(null);

    let metadata: MultisectionMetadata = getContext("metadata");
</script>

<Menu />
<div class="horizontal-centering">
    <div class="vertical-flow">
        {#each Object.entries(metadata.sections) as [sectionKey, section]}
            <div class="section-container">
                <h1>{section.title[$textSourcesConfigStore[sectionKey].main]}</h1>
                {#if section.subtitle}
                    <p>{section.subtitle[$textSourcesConfigStore[sectionKey].main]}</p>
                {/if}
                <div class="cards-container">
                    {#each section.books as bookInfo}
                        <TanakhBookCard
                            {sectionKey}
                            {bookInfo}
                            sectionParshaInfos={section.parshas}
                            availableParshaId={metadata.available_parsha}
                        />
                    {/each}
                </div>
            </div>
        {/each}
    </div>
</div>

<style>
    .horizontal-centering {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .vertical-flow {
        min-width: 40vw;
        max-width: 100%;
        margin-top: 4em;
    }
    .section-container {
        margin-top: 2em;
    }

    h1 {
        margin-bottom: 0.5em;
    }

    .cards-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
</style>
