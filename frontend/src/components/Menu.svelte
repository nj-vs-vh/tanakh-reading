<script lang="ts">
    import { Link } from "svelte-routing";
    import Icon from "./shared/Icon.svelte";
    import InlineIcon from "./shared/InlineIcon.svelte";
    import BurgerMenu from "./shared/BurgerMenu/BurgerMenu.svelte";
    import {
        commentSourceFlagsStore,
        toggleCommentSourceFlag,
    } from "../settings/commentSources";
    import type { CommentSourceFlags } from "../settings/commentSources";
    import { getContext } from "svelte";
    import type { Metadata } from "../types";
    import {
        TextDecorationStyle,
        textDecorationStyleStore,
        setTextDecorationStyle,
    } from "../settings/textDecorationStyle";
    import {
        CommentStyle,
        commentStyleStore,
        setCommentStyle,
    } from "../settings/commentStyle";
    import {
        enableTextSource,
        setMainTextSource,
        textSourcesConfigStore,
        toggleTextSourceEnabled,
    } from "../settings/textSources";

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

    let mainTextSource: string;
    let enabledTextSources: Record<string, boolean>;
    textSourcesConfigStore.subscribe((config) => {
        mainTextSource = config.main;
        enabledTextSources = config.enabledInDetails;
    });
    function setMainTextSourceFromEvent(e) {
        const source = e.target.value;
        setMainTextSource(source);
        enableTextSource(source);
    }

    const metadata: Metadata = getContext("metadata");

    export let homeButton: boolean = false;

    const backgroundColor = "#dddddd";

    let commentSettingsFolded = true;
    function toggleCommentSettingsFolded(e) {
        commentSettingsFolded = !commentSettingsFolded;
    }

    let textSettingsFolded = true;
    function toggleTextSettingsFolded(e) {
        textSettingsFolded = !textSettingsFolded;
    }
</script>

<BurgerMenu
    duration={0.2}
    width="400px"
    {backgroundColor}
    burgerColor={backgroundColor}
    menuColor="black"
    padding="10px"
    paddingTop="60px"
>
    <div class="inner-container">
        {#if homeButton}
            <Link to="/">
                <h2>
                    <div class="nav-icon">
                        <InlineIcon heightEm={0.8}>
                            <Icon icon="synagogue" color="black" />
                        </InlineIcon>
                    </div>
                    <span class="nav-caption">Оглавление</span>
                </h2>
            </Link>
        {/if}

        <h2
            on:click={toggleTextSettingsFolded}
            on:keydown={toggleTextSettingsFolded}
        >
            <div class="nav-icon">
                <InlineIcon heightEm={0.8}>
                    <Icon icon="torah-scroll" color="black" />
                </InlineIcon>
            </div>
            <span class="nav-caption">Текст</span>
        </h2>
        <div class={textSettingsFolded ? "folded" : ""}>
            <div class="settings-block">
                <h4>Основной</h4>
                {#each metadata.text_sources as textSource}
                    <div class="input-with-label">
                        <input
                            type="radio"
                            name="mainTextSource"
                            value={textSource}
                            checked={mainTextSource == textSource}
                            on:change={setMainTextSourceFromEvent}
                        />
                        <label for={textSource}>
                            <span>
                                <span class="text-source-short-name">
                                    {metadata.text_source_marks[textSource]}
                                </span>
                                <span>
                                    {metadata.text_source_descriptions[
                                        textSource
                                    ]}
                                </span>
                                {#each Array.from(metadata.text_source_links[textSource].entries()) as [index, link]}
                                    <sup>
                                        <a
                                            href={link}
                                            target="_blank"
                                            rel="noreferrer"
                                            class="external-link"
                                        >
                                            {index + 1}
                                        </a>
                                    </sup>
                                {/each}
                            </span>
                        </label>
                    </div>
                {/each}
            </div>
            <div class="settings-block">
                <h4>В окне с комментариями</h4>
                {#each Object.entries(enabledTextSources) as [source, isActive]}
                    <div class="input-with-label">
                        <input
                            type="checkbox"
                            id={`${source}-in-comments`}
                            name={`${source}-in-comments`}
                            checked={isActive || source === mainTextSource}
                            on:change|preventDefault={(e) => {
                                if (source === mainTextSource) {
                                    // @ts-ignore
                                    e.target.checked = true;
                                    enableTextSource(source);
                                } else {
                                    // @ts-ignore
                                    toggleTextSourceEnabled(source);
                                }
                            }}
                        />
                        <label for={`${source}-in-comments`}>
                            {metadata.text_source_marks[source]}
                        </label>
                    </div>
                {/each}
            </div>
        </div>

        <h2
            on:click={toggleCommentSettingsFolded}
            on:keydown={toggleCommentSettingsFolded}
        >
            <div class="nav-icon">
                <InlineIcon heightEm={0.8}>
                    <Icon icon="comment" color="black" />
                </InlineIcon>
            </div>
            <span class="nav-caption">Комментарии</span>
        </h2>
        <div class={commentSettingsFolded ? "folded" : ""}>
            <div class="settings-block">
                <h4>Авторы</h4>
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
                                {#each Array.from(metadata.commenter_links[commenter].entries()) as [index, link]}
                                    <sup>
                                        <a
                                            href={link}
                                            target="_blank"
                                            rel="noreferrer"
                                            class="external-link"
                                        >
                                            {index + 1}
                                        </a>
                                    </sup>
                                {/each}
                            </span>
                        </label>
                    </div>
                {/each}
                <div class="input-with-label">
                    <input
                        type="checkbox"
                        id="all"
                        name="all"
                        checked={Object.values(commentSourceFlags).reduce(
                            (f1, f2) => f1 & f2,
                            true
                        )}
                        on:change={(e) => {
                            const newFlags = new Map();
                            for (const commenter of Object.keys(
                                commentSourceFlags
                            )) {
                                // @ts-ignore
                                newFlags[commenter] = e.target.checked;
                            }
                            commentSourceFlagsStore.set(newFlags);
                        }}
                    />
                    <label for="all">Все</label>
                </div>
            </div>
            <div class="settings-block">
                <h4>Стиль аннотаций</h4>
                <div class="input-with-label">
                    <input
                        type="radio"
                        id={TextDecorationStyle.ASTRERISK}
                        name="textDecorationStyle"
                        value={TextDecorationStyle.ASTRERISK}
                        checked={textDecorationStyle ==
                            TextDecorationStyle.ASTRERISK}
                        on:change={setTextDecorationStyleFromEvent}
                    />
                    <label for={TextDecorationStyle.ASTRERISK}>
                        <span>Звёздочки</span>
                        <InlineIcon heightEm={0.7}>
                            <Icon icon={"asterisk"} color={"#606060"} />
                        </InlineIcon>
                    </label>
                </div>
                <div class="input-with-label">
                    <input
                        type="radio"
                        id={TextDecorationStyle.CLICKABLE_TEXT}
                        name="textDecorationStyle"
                        value={TextDecorationStyle.CLICKABLE_TEXT}
                        checked={textDecorationStyle ==
                            TextDecorationStyle.CLICKABLE_TEXT}
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
                        checked={textDecorationStyle ==
                            TextDecorationStyle.NONE}
                        on:change={setTextDecorationStyleFromEvent}
                    />
                    <label for={TextDecorationStyle.NONE}>
                        <span>Нет</span>
                    </label>
                </div>
            </div>
            <div class="settings-block">
                <h4>Стиль комментариев</h4>
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
            </div>
        </div>
    </div>
</BurgerMenu>

<style>
    .inner-container {
        max-width: calc(90vw - 1.5em);
        padding-right: 1.5em;
    }

    h2 {
        margin: 0.4em 0 0.4em 0;
        display: flex;
        flex-direction: row;
        align-items: center;
        cursor: pointer;
    }

    h2:hover {
        text-decoration: underline;
    }

    h4 {
        margin: 0 0 0.2em 0;
    }

    input {
        margin-left: 0;
    }

    label {
        margin-left: 0.2em;
    }

    .nav-caption {
        margin-left: 0.3em;
    }

    .nav-icon {
        display: flex;
        justify-content: center;
        align-items: center;
        min-width: 1.5em;
    }

    .folded {
        display: none;
        height: 0;
    }

    .settings-block {
        margin-top: 1em;
        padding-left: 1em;
        margin-left: 1em;
        border-left: 1px black solid;
        font-size: large;
    }

    a.external-link {
        color: rgb(52, 52, 66);
        padding: 0 0.2em;
        text-decoration: underline;
    }

    a.external-link:hover {
        color: rgb(39, 39, 139);
    }

    span.text-source-short-name {
        color: grey;
    }

    div.input-with-label {
        display: flex;
        align-items: baseline;
        padding: 0.2em 0;
    }
</style>
