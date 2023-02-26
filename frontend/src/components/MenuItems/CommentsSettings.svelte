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
        setCommentFilterByBookmarkMode,
        CommentFilterByBookmarkMode,
        swapElementsInSourceOrder as moveElementInSourceOrder,
    } from "../../settings/commentSources";
    import type { Metadata } from "../../types";
    import Icon from "../shared/Icon.svelte";

    const metadata: Metadata = getContext("metadata");
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
            {#each initialSourcesOrder as commentSource}
                <div class="input-with-label">
                    <div class="checkbox-with-grip">
                        <input
                            type="checkbox"
                            id={commentSource}
                            name={commentSource}
                            checked={$commentSourcesConfigStore.filterBySource[commentSource]}
                            on:change={() => toggleCommentFilterBySource(commentSource)}
                        />
                        <div class="grip-handle-container">
                            <Icon icon="grip" heightEm={1} />
                        </div>
                    </div>
                    <label for={commentSource}>
                        <span>
                            <span>
                                {metadata.commenter_names[commentSource]}
                            </span>
                            <WikiStyleLinks urls={metadata.commenter_links[commentSource]} />
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
    {#if metadata.logged_in_user !== null}
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
    {/if}
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
