<script lang="ts">
    import type { MultisectionMetadata } from "../../types";
    import {
        enableTextSource,
        setMainTextSource,
        textSourcesConfigStore,
        toggleTextSourceEnabled,
    } from "../../settings/textSources";
    import MenuFolder from "./MenuFolder.svelte";
    import MenuFolderBlock from "./MenuFolderBlock.svelte";
    import WikiStyleLinks from "./WikiStyleLinks.svelte";

    export let metadata: MultisectionMetadata;
</script>

<MenuFolder icon="torah-scroll" title="Текст">
    {#each Object.entries(metadata.sections) as [sectionKey, section]}
        <h3 class="section-title">{section.title[$textSourcesConfigStore[sectionKey].main]}</h3>
        <MenuFolderBlock title="Основной">
            {#each section.text_sources as textSource}
                <div class="input-with-label">
                    <input
                        type="radio"
                        id={`select-main-${textSource.key}`}
                        name={`select-main-${textSource.key}`}
                        checked={$textSourcesConfigStore[sectionKey].main === textSource.key}
                        on:change={() => {
                            setMainTextSource(sectionKey, textSource.key);
                            enableTextSource(sectionKey, textSource.key);
                        }}
                    />
                    <label for={`select-main-${textSource.key}`}>
                        <span>
                            <span class="text-source-short-name">
                                {textSource.mark}
                            </span>
                            <span>
                                {textSource.description}
                            </span>
                            <WikiStyleLinks urls={textSource.links} />
                        </span>
                    </label>
                </div>
            {/each}
        </MenuFolderBlock>
        <MenuFolderBlock title="В окне с комментариями">
            {#each Object.entries($textSourcesConfigStore[sectionKey].enabledInDetails) as [textSourceKey, isActive]}
                <div class="input-with-label">
                    <input
                        type="checkbox"
                        id={`${textSourceKey}-in-comments`}
                        name={`${textSourceKey}-in-comments`}
                        checked={isActive || textSourceKey === $textSourcesConfigStore[sectionKey].main}
                        on:change|preventDefault={(e) => {
                            if (textSourceKey === $textSourcesConfigStore[sectionKey].main) {
                                // @ts-expect-error
                                e.target.checked = true;
                                enableTextSource(sectionKey, textSourceKey);
                            } else {
                                toggleTextSourceEnabled(sectionKey, textSourceKey);
                            }
                        }}
                    />
                    <label for={`${textSourceKey}-in-comments`}>
                        {section.text_sources.find((textSource) => textSource.key == textSourceKey).mark}
                    </label>
                </div>
            {/each}
        </MenuFolderBlock>
    {/each}
</MenuFolder>

<style>
    h3.section-title {
        margin-left: 0.7em;
        margin-bottom: 0.7em;
        margin-top: 1em;
        font-size: larger;
    }
    span.text-source-short-name {
        color: var(--theme-color-secondary-text);
    }
</style>
