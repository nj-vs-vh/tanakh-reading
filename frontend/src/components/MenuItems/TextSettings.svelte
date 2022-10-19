<script lang="ts">
    import { getContext } from "svelte";
    import type { Metadata } from "../../types";
    import {
        enableTextSource,
        setMainTextSource,
        textSourcesConfigStore,
        toggleTextSourceEnabled,
    } from "../../settings/textSources";
    import MenuFolder from "./MenuFolder.svelte";
    import MenuFolderBlock from "./MenuFolderBlock.svelte";
    import WikiStyleLinks from "./WikiStyleLinks.svelte";

    let mainTextSource: string;
    let enabledTextSources: Record<string, boolean>;
    textSourcesConfigStore.subscribe((config) => {
        mainTextSource = config.main;
        enabledTextSources = config.enabledInDetails;
    });
    function setMainTextSourceFromEvent(e) {
        const source = e.target.value;
        setMainTextSource(source);
        enableTextSource(source);
    }

    const metadata: Metadata = getContext("metadata");
</script>

<MenuFolder icon="torah-scroll" title="Текст">
    <MenuFolderBlock title="Основной">
        {#each metadata.text_sources as textSource}
            <div class="input-with-label">
                <input
                    type="radio"
                    name="mainTextSource"
                    id={textSource}
                    value={textSource}
                    checked={mainTextSource == textSource}
                    on:change={setMainTextSourceFromEvent}
                />
                <label for={textSource}>
                    <span>
                        <span class="text-source-short-name">
                            {metadata.text_source_marks[textSource]}
                        </span>
                        <span>
                            {metadata.text_source_descriptions[textSource]}
                        </span>
                        <WikiStyleLinks
                            urls={metadata.text_source_links[textSource]}
                        />
                    </span>
                </label>
            </div>
        {/each}
    </MenuFolderBlock>
    <MenuFolderBlock title="В окне с комментариями">
        {#each Object.entries(enabledTextSources) as [source, isActive]}
            <div class="input-with-label">
                <input
                    type="checkbox"
                    id={`${source}-in-comments`}
                    name={`${source}-in-comments`}
                    checked={isActive || source === mainTextSource}
                    on:change|preventDefault={(e) => {
                        if (source === mainTextSource) {
                            // @ts-ignore
                            e.target.checked = true;
                            enableTextSource(source);
                        } else {
                            // @ts-ignore
                            toggleTextSourceEnabled(source);
                        }
                    }}
                />
                <label for={`${source}-in-comments`}>
                    {metadata.text_source_marks[source]}
                </label>
            </div>
        {/each}
    </MenuFolderBlock>
</MenuFolder>

<style>
    span.text-source-short-name {
        color: grey;
    }
</style>
