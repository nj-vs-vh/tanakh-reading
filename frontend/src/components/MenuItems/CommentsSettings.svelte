<script lang="ts">
    import { getContext } from "svelte";
    import MenuFolder from "./MenuFolder.svelte";
    import MenuFolderBlock from "./MenuFolderBlock.svelte";
    import WikiStyleLinks from "./WikiStyleLinks.svelte";

    import {
        commentSourcesConfigStore,
        toggleCommentFilterBySource,
        setCommentFilterBySource,
        setCommentFilterByBookmarkMode,
        CommentFilterByBookmarkMode,
    } from "../../settings/commentSources";
    import type { Metadata } from "../../types";

    const metadata: Metadata = getContext("metadata");
</script>

<MenuFolder icon="tanakh-book" title="Комментарии">
    <MenuFolderBlock title="Фильтр по авторам">
        {#each Object.entries($commentSourcesConfigStore.filterBySource) as [commentSource, isActive]}
            <div class="input-with-label">
                <input
                    type="checkbox"
                    id={commentSource}
                    name={commentSource}
                    checked={isActive}
                    on:change={() => toggleCommentFilterBySource(commentSource)}
                />
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
