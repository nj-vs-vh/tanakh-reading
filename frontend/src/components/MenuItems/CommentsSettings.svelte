<script lang="ts">
    import { SortableList } from "@jhubbardsf/svelte-sortablejs";

    import MenuFolder from "./MenuFolder.svelte";
    import MenuFolderBlock from "./MenuFolderBlock.svelte";
    import WikiStyleLinks from "./WikiStyleLinks.svelte";

    import {
        commentSourcesConfigStore,
        toggleCommentFilterBySource,
        setCommentFilterBySource,
        swapElementsInSourceOrder as moveElementInSourceOrder,
    } from "../../settings/commentSources";
    import { textSourcesConfigStore } from "../../settings/textSources";
    import type { MultisectionMetadata, SectionKey } from "../../types";
    import Icon from "../shared/Icon.svelte";

    export let metadata: MultisectionMetadata;
    export let sectionKey: SectionKey | undefined;

    const sectionKeyDefined = sectionKey !== undefined;
    let sectionsWithComments = Object.entries(metadata.sections).filter(
        ([_, section]) => section.comment_sources.length > 0,
    );
    if (sectionKeyDefined) {
        sectionsWithComments = sectionsWithComments.filter(([sk, _]) => sk === sectionKey);
    }
    const initialSourceConfig = $commentSourcesConfigStore;
</script>

{#if sectionsWithComments.length > 0}
    <MenuFolder icon="tanakh-book" title="Комментарии">
        {#each sectionsWithComments as [sectionKey, section]}
            {#if !sectionKeyDefined}
                <h3 class="section-title">{section.title[$textSourcesConfigStore[sectionKey].main]}</h3>
            {/if}
            <MenuFolderBlock title="Фильтр по авторам">
                <SortableList
                    class="sortable-class-unused"
                    handle=".checkbox-with-grip"
                    onSort={(e) => {
                        moveElementInSourceOrder(sectionKey, e.oldIndex, e.newIndex);
                    }}
                >
                    {#each initialSourceConfig[sectionKey].sourcesOrder as commentSourceKey}
                        <div class="input-with-label">
                            <div class="checkbox-with-grip">
                                <input
                                    type="checkbox"
                                    id={commentSourceKey}
                                    name={commentSourceKey}
                                    checked={$commentSourcesConfigStore[sectionKey].filterBySource[commentSourceKey]}
                                    on:change={() => toggleCommentFilterBySource(sectionKey, commentSourceKey)}
                                />
                                <div class="grip-handle-container">
                                    <Icon icon="grip" heightEm={1} />
                                </div>
                            </div>
                            <label for={commentSourceKey}>
                                <span>
                                    <span>
                                        {section.comment_sources.find(
                                            (commentSource) => commentSource.key === commentSourceKey,
                                        ).name}
                                    </span>
                                    <WikiStyleLinks
                                        urls={section.comment_sources.find(
                                            (commentSource) => commentSource.key === commentSourceKey,
                                        ).links}
                                    />
                                </span>
                            </label>
                        </div>
                    {/each}
                </SortableList>
                <div class="input-with-label">
                    <input
                        type="checkbox"
                        id="all"
                        name="all"
                        checked={Object.values($commentSourcesConfigStore[sectionKey].filterBySource).reduce(
                            (f1, f2) => f1 && f2,
                            true,
                        )}
                        on:change={(e) => {
                            const newFilterBySource = {};
                            for (const commentSource of Object.keys(
                                $commentSourcesConfigStore[sectionKey].filterBySource,
                            )) {
                                // @ts-expect-error
                                newFilterBySource[commentSource] = e.target.checked;
                            }
                            setCommentFilterBySource(sectionKey, newFilterBySource);
                        }}
                    />
                    <label for="all">Все</label>
                </div>
            </MenuFolderBlock>
            <!-- NOTE: filter by bookmark status is disabled -->
            <!-- {#if metadata.logged_in_user !== null}
        <MenuFolderBlock title="Фильтр по закладкам">
            {#each Object.values(CommentFilterByBookmarkMode) as mode}
                <div class="input-with-label">
                    <input
                        type="radio"
                        id={mode}
                        name={mode}
                        checked={mode == $commentSourcesConfigStore[sectionKey].filterByBookmarkMode}
                        on:change={(e) => {
                            // @ts-ignore
                            setCommentFilterByBookmarkMode(e.target.name);
                        }}
                    />
                    <label for={mode}>{mode}</label>
                </div>
            {/each}
        </MenuFolderBlock>
        {/if} -->
        {/each}
    </MenuFolder>
{/if}

<style>
    .grip-handle-container {
        cursor: grab;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .grip-handle-container:active {
        cursor: grabbing;
    }

    h3.section-title {
        margin-left: 0.7em;
        margin-bottom: 0.7em;
        margin-top: 1em;
        font-size: larger;
    }
</style>
