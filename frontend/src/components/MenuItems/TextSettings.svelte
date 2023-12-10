<script lang="ts">
    import { getContext, onDestroy } from "svelte";
    import type { SectionMetadata } from "../../types";
    import {
        enableTextSource,
        setMainTextSource,
        textSourcesConfigStore,
        toggleTextSourceEnabled,
    } from "../../settings/textSources";
    import MenuFolder from "./MenuFolder.svelte";
    import MenuFolderBlock from "./MenuFolderBlock.svelte";
    import WikiStyleLinks from "./WikiStyleLinks.svelte";

    let mainTextSourceKey: string;
    let enabledTextSources: Record<string, boolean>;
    const textSourcesConfigStoreUnsubscribe = textSourcesConfigStore.subscribe((config) => {
        mainTextSourceKey = config.main;
        enabledTextSources = config.enabledInDetails;
    });

    function setMainTextSourceFromEvent(e) {
        const source = e.target.value;
        setMainTextSource(source);
        enableTextSource(source);
    }

    const metadata: SectionMetadata = getContext("metadata");
    const textSourceByKey = Object.fromEntries(metadata.section.text_sources.map(ts => [ts.key, ts]))

    onDestroy(textSourcesConfigStoreUnsubscribe);
</script>

<MenuFolder icon="torah-scroll" title="Текст">
    <MenuFolderBlock title="Основной">
        {#each metadata.section.text_sources as textSource}
            <div class="input-with-label">
                <input
                    type="radio"
                    name="mainTextSource"
                    id={textSource.key}
                    value={textSource.key}
                    checked={mainTextSourceKey == textSource.key}
                    on:change={setMainTextSourceFromEvent}
                />
                <label for={textSource.key}>
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
        {#each Object.entries(enabledTextSources) as [textSourceKey, isActive]}
            <div class="input-with-label">
                <input
                    type="checkbox"
                    id={`${textSourceKey}-in-comments`}
                    name={`${textSourceKey}-in-comments`}
                    checked={isActive || textSourceKey === mainTextSourceKey}
                    on:change|preventDefault={(e) => {
                        if (textSourceKey === mainTextSourceKey) {
                            // @ts-expect-error
                            e.target.checked = true;
                            enableTextSource(textSourceKey);
                        } else {
                            toggleTextSourceEnabled(textSourceKey);
                        }
                    }}
                />
                <label for={`${textSourceKey}-in-comments`}>
                    {textSourceByKey[textSourceKey].mark}
                </label>
            </div>
        {/each}
    </MenuFolderBlock>
</MenuFolder>

<style>
    span.text-source-short-name {
        color: var(--theme-color-secondary-text);
    }
</style>
