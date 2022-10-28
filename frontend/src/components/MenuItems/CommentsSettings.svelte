<script lang="ts">
    import Icon from "../shared/Icon.svelte";
    import { commentSourceFlagsStore, toggleCommentSourceFlag } from "../../settings/commentSources";
    import type { CommentSourceFlags } from "../../settings/commentSources";
    import { getContext } from "svelte";
    import type { Metadata } from "../../types";
    import {
        TextDecorationStyle,
        textDecorationStyleStore,
        setTextDecorationStyle,
    } from "../../settings/textDecorationStyle";
    import { CommentStyle, commentStyleStore, setCommentStyle } from "../../settings/commentStyle";
    import MenuFolder from "./MenuFolder.svelte";
    import MenuFolderBlock from "./MenuFolderBlock.svelte";
    import WikiStyleLinks from "./WikiStyleLinks.svelte";

    let commentSourceFlags: CommentSourceFlags;
    commentSourceFlagsStore.subscribe((v) => {
        commentSourceFlags = v;
    });
    let textDecorationStyle: TextDecorationStyle;
    textDecorationStyleStore.subscribe((v) => {
        textDecorationStyle = v;
    });
    function setTextDecorationStyleFromEvent(e) {
        setTextDecorationStyle(e.target.value);
    }

    let commentStyle: CommentStyle;
    commentStyleStore.subscribe((v) => {
        commentStyle = v;
    });
    function setCommentStyleFromEvent(e) {
        setCommentStyle(e.target.value);
    }

    const metadata: Metadata = getContext("metadata");
</script>

<MenuFolder icon="comment" title="Комментарии">
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
    <MenuFolderBlock title="Стиль аннотаций">
        <div class="input-with-label">
            <input
                type="radio"
                id={TextDecorationStyle.ASTRERISK}
                name="textDecorationStyle"
                value={TextDecorationStyle.ASTRERISK}
                checked={textDecorationStyle == TextDecorationStyle.ASTRERISK}
                on:change={setTextDecorationStyleFromEvent}
            />
            <label for={TextDecorationStyle.ASTRERISK}>
                <span>Звёздочки</span>
                <Icon heightEm={0.7} icon={"asterisk"} color={"#606060"} />
            </label>
        </div>
        <div class="input-with-label">
            <input
                type="radio"
                id={TextDecorationStyle.CLICKABLE_TEXT}
                name="textDecorationStyle"
                value={TextDecorationStyle.CLICKABLE_TEXT}
                checked={textDecorationStyle == TextDecorationStyle.CLICKABLE_TEXT}
                on:change={setTextDecorationStyleFromEvent}
            />
            <label for={TextDecorationStyle.CLICKABLE_TEXT}>
                <span>
                    <span class="clickable">Нажимаемый текст </span>
                </span>
            </label>
        </div>
        <div class="input-with-label">
            <input
                type="radio"
                id={TextDecorationStyle.NONE}
                name="textDecorationStyle"
                value={TextDecorationStyle.NONE}
                checked={textDecorationStyle == TextDecorationStyle.NONE}
                on:change={setTextDecorationStyleFromEvent}
            />
            <label for={TextDecorationStyle.NONE}>
                <span>Нет</span>
            </label>
        </div>
    </MenuFolderBlock>
    <MenuFolderBlock title="Стиль комментариев">
        <div class="input-with-label">
            <input
                type="radio"
                id={CommentStyle.MODAL}
                name="commentStyle"
                value={CommentStyle.MODAL}
                checked={commentStyle == CommentStyle.MODAL}
                on:change={setCommentStyleFromEvent}
            />
            <label for={CommentStyle.MODAL}> Окно </label>
        </div>
        <div class="input-with-label">
            <input
                type="radio"
                id={CommentStyle.INLINE}
                name="commentStyle"
                value={CommentStyle.INLINE}
                checked={commentStyle == CommentStyle.INLINE}
                on:change={setCommentStyleFromEvent}
            />
            <label for={CommentStyle.INLINE}> В тексте </label>
        </div>
    </MenuFolderBlock>
</MenuFolder>
