<script lang="ts">
    import { getContext } from "svelte";
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
    import type { SectionMetadata } from "../../types";
    import Icon from "../shared/Icon.svelte";

    const metadata: SectionMetadata = getContext("metadata");
    const commentSourceByKey = Object.fromEntries(metadata.section.comment_sources.map(cs => [cs.key, cs]));
    const initialSourcesOrder = $commentSourcesConfigStore.sourcesOrder;
</script>

<MenuFolder icon="tanakh-book" title="Комментарии">
    <MenuFolderBlock title="Фильтр по авторам">
        <SortableList
            class="sortable-class-unused"
            handle=".checkbox-with-grip"
            onSort={(e) => {
                moveElementInSourceOrder(e.oldIndex, e.newIndex);
            }}
        >
            {#each initialSourcesOrder as commentSourceKey}
                <div class="input-with-label">
                    <div class="checkbox-with-grip">
                        <input
                            type="checkbox"
                            id={commentSourceKey}
                            name={commentSourceKey}
                            checked={$commentSourcesConfigStore.filterBySource[commentSourceKey]}
                            on:change={() => toggleCommentFilterBySource(commentSourceKey)}
                        />
                        <div class="grip-handle-container">
                            <Icon icon="grip" heightEm={1} />
                        </div>
                    </div>
                    <label for={commentSourceKey}>
                        <span>
                            <span>
                                {commentSourceByKey[commentSourceKey].name}
                            </span>
                            <WikiStyleLinks urls={commentSourceByKey[commentSourceKey].links} />
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
                checked={Object.values($commentSourcesConfigStore.filterBySource).reduce((f1, f2) => f1 && f2, true)}
                on:change={(e) => {
                    const newFilterBySource = {};
                    for (const commentSource of Object.keys($commentSourcesConfigStore.filterBySource)) {
                        // @ts-ignore
                        newFilterBySource[commentSource] = e.target.checked;
                    }
                    setCommentFilterBySource(newFilterBySource);
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
                        checked={mode == $commentSourcesConfigStore.filterByBookmarkMode}
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
</MenuFolder>

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
</style>
