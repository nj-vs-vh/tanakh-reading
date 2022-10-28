<script lang="ts">
    import { getContext } from "svelte";
    import MenuFolder from "./MenuFolder.svelte";
    import MenuFolderBlock from "./MenuFolderBlock.svelte";
    import WikiStyleLinks from "./WikiStyleLinks.svelte";

    import { commentSourceFlagsStore, toggleCommentSourceFlag } from "../../settings/commentSources";
    import type { CommentSourceFlags } from "../../settings/commentSources";
    import type { Metadata } from "../../types";

    let commentSourceFlags: CommentSourceFlags;
    commentSourceFlagsStore.subscribe((v) => {
        commentSourceFlags = v;
    });

    const metadata: Metadata = getContext("metadata");
</script>

<MenuFolder icon="tanakh-book" title="Комментарии">
    <MenuFolderBlock title="Авторы">
        {#each Object.entries(commentSourceFlags) as [commenter, isActive]}
            <div class="input-with-label">
                <input
                    type="checkbox"
                    id={commenter}
                    name={commenter}
                    checked={isActive}
                    on:change={(e) => {
                        toggleCommentSourceFlag(commenter);
                    }}
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
                checked={Object.values(commentSourceFlags).reduce((f1, f2) => f1 & f2, true)}
                on:change={(e) => {
                    const newFlags = new Map();
                    for (const commenter of Object.keys(commentSourceFlags)) {
                        // @ts-ignore
                        newFlags[commenter] = e.target.checked;
                    }
                    commentSourceFlagsStore.set(newFlags);
                }}
            />
            <label for="all">Все</label>
        </div>
    </MenuFolderBlock>
</MenuFolder>
