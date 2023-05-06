<script lang="ts">
    import { getContext } from "svelte";

    import Icon from "../shared/Icon.svelte";
    import MenuFolder from "./MenuFolder.svelte";
    import MenuFolderBlock from "./MenuFolderBlock.svelte";

    import {
        TextDecorationStyle,
        textDecorationStyleStore,
        setTextDecorationStyle,
    } from "../../settings/textDecorationStyle";
    import { CommentStyle, commentStyleStore, setCommentStyle } from "../../settings/commentStyle";
    import {
        setTextDecorationSettings,
        TextDecorationSettings,
        textDecorationSettingsStore,
    } from "../../settings/textDecorationSettings";
    import { onDestroy } from "svelte";

    // @ts-ignore
    let { toggle, current } = getContext("theme");

    function setTextDecorationStyleFromEvent(e) {
        setTextDecorationStyle(e.target.value);
    }

    function setCommentStyleFromEvent(e) {
        setCommentStyle(e.target.value);
    }

    let onlyDecorateTextWithComments: boolean;
    let textDecorationSettings: TextDecorationSettings;
    const textDecorationSettingsStoreUnsubscribe = textDecorationSettingsStore.subscribe((v) => {
        textDecorationSettings = v;
        onlyDecorateTextWithComments = v.onlyDecorateTextWithComments;
    });

    onDestroy(textDecorationSettingsStoreUnsubscribe);
</script>

<MenuFolder icon="sliders" title="Настройки">
    <MenuFolderBlock title="Общие">
        <div class="input-with-label">
            <input
                type="checkbox"
                id="onlyDecorateTextWithCommentsCheckbox"
                name="onlyDecorateTextWithComments"
                checked={onlyDecorateTextWithComments}
                on:change={(e) => {
                    setTextDecorationSettings({
                        ...textDecorationSettings,
                        // @ts-ignore
                        onlyDecorateTextWithComments: e.target.checked,
                    });
                }}
            />
            <label for="onlyDecorateTextWithCommentsCheckbox">
                <span>Разметка только для стихов с комментариями</span>
                <span class="description">(учитывая фильтры)</span>
            </label>
        </div>
    </MenuFolderBlock>
    <MenuFolderBlock title="Стиль разметки">
        <div class="input-with-label">
            <input
                type="radio"
                id={TextDecorationStyle.ASTRERISK}
                name="textDecorationStyle"
                value={TextDecorationStyle.ASTRERISK}
                checked={$textDecorationStyleStore == TextDecorationStyle.ASTRERISK}
                on:change={setTextDecorationStyleFromEvent}
            />
            <label for={TextDecorationStyle.ASTRERISK}>
                <span>Звёздочки</span>
                <Icon heightEm={0.7} icon={"asterisk"} color={"var(--theme-color-secondary-text)"} />
            </label>
        </div>
        <div class="input-with-label">
            <input
                type="radio"
                id={TextDecorationStyle.CLICKABLE_TEXT}
                name="textDecorationStyle"
                value={TextDecorationStyle.CLICKABLE_TEXT}
                checked={$textDecorationStyleStore == TextDecorationStyle.CLICKABLE_TEXT}
                on:change={setTextDecorationStyleFromEvent}
            />
            <label for={TextDecorationStyle.CLICKABLE_TEXT}>
                <span>
                    <span class="clickable">Нажимаемый текст стиха</span>
                </span>
            </label>
        </div>
        <div class="input-with-label">
            <input
                type="radio"
                id={TextDecorationStyle.NONE}
                name="textDecorationStyle"
                value={TextDecorationStyle.NONE}
                checked={$textDecorationStyleStore == TextDecorationStyle.NONE}
                on:change={setTextDecorationStyleFromEvent}
            />
            <label for={TextDecorationStyle.NONE}>
                <span>Нет</span>
            </label>
        </div>
    </MenuFolderBlock>
    <MenuFolderBlock title="Комментарии">
        <div class="input-with-label">
            <input
                type="radio"
                id={CommentStyle.MODAL}
                name="commentStyle"
                value={CommentStyle.MODAL}
                checked={$commentStyleStore == CommentStyle.MODAL}
                on:change={setCommentStyleFromEvent}
            />
            <label for={CommentStyle.MODAL}>В окне</label>
        </div>
        <div class="input-with-label">
            <input
                type="radio"
                id={CommentStyle.INLINE}
                name="commentStyle"
                value={CommentStyle.INLINE}
                checked={$commentStyleStore == CommentStyle.INLINE}
                on:change={setCommentStyleFromEvent}
            />
            <label for={CommentStyle.INLINE}>
                <span>В тексте</span>
                <span class="description">(без вариантов перевода)</span>
            </label>
        </div>
    </MenuFolderBlock>
    <MenuFolderBlock title="Тема">
        <button on:click={toggle} style="width: 100%; padding: 0.5em;">
            {$current}
        </button>
    </MenuFolderBlock>
</MenuFolder>

<style>
    span.description {
        color: var(--theme-color-secondary-text);
    }
</style>
