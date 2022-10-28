<script lang="ts">
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

    let onlyDecorateTextWithComments: boolean;
    let textDecorationSettings: TextDecorationSettings;
    textDecorationSettingsStore.subscribe((v) => {
        textDecorationSettings = v;
        onlyDecorateTextWithComments = v.onlyDecorateTextWithComments;
    });
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
                checked={textDecorationStyle == TextDecorationStyle.NONE}
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
                checked={commentStyle == CommentStyle.MODAL}
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
                checked={commentStyle == CommentStyle.INLINE}
                on:change={setCommentStyleFromEvent}
            />
            <label for={CommentStyle.INLINE}>
                <span>В тексте</span>
                <span class="description">(без вариантов перевода)</span>
            </label>
        </div>
    </MenuFolderBlock>
</MenuFolder>

<style>
    span.description {
        color: grey;
    }
</style>
