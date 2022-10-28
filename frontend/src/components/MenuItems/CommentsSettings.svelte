<script lang="ts">
    import { getContext } from "svelte";
    import MenuFolder from "./MenuFolder.svelte";
    import MenuFolderBlock from "./MenuFolderBlock.svelte";
    import WikiStyleLinks from "./WikiStyleLinks.svelte";

    import {
        commentFiltersStore,
        toggleCommentFilterBySource,
        setCommentFilterBySource,
        setCommentFilterByBookmarkMode,
        CommentFilterByBookmarkMode,
    } from "../../settings/commentFilters";
    import type { CommentFilters } from "../../settings/commentFilters";
    import type { Metadata } from "../../types";

    let commentFilters: CommentFilters;
    commentFiltersStore.subscribe((v) => {
        commentFilters = v;
    });

    const metadata: Metadata = getContext("metadata");
</script>

<MenuFolder icon="tanakh-book" title="Комментарии">
    <MenuFolderBlock title="Фильтр по авторам">
        {#each Object.entries(commentFilters.bySource) as [commenter, isActive]}
            <div class="input-with-label">
                <input
                    type="checkbox"
                    id={commenter}
                    name={commenter}
                    checked={isActive}
                    on:change={() => toggleCommentFilterBySource(commenter)}
                />
                <label for={commenter}>
                    <span>
                        <span>
                            {metadata.commenter_names[commenter]}
                        </span>
                        <WikiStyleLinks urls={metadata.commenter_links[commenter]} />
                    </span>
                </label>
            </div>
        {/each}
        <div class="input-with-label">
            <input
                type="checkbox"
                id="all"
                name="all"
                checked={Object.values(commentFilters.bySource).reduce((f1, f2) => f1 && f2, true)}
                on:change={(e) => {
                    const newFilterBySource = {};
                    for (const commenter of Object.keys(commentFilters.bySource)) {
                        // @ts-ignore
                        newFilterBySource[commenter] = e.target.checked;
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
                        checked={mode == commentFilters.byBookmarkMode}
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
