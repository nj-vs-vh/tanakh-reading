<script lang="ts">
    import { Link } from "svelte-routing";
    import Icon from "./shared/Icon.svelte";
    import InlineIcon from "./shared/InlineIcon.svelte";
    import BurgerMenu from "./shared/BurgerMenu/BurgerMenu.svelte";
    import {
        commentSourceFlagsStore,
        toggleCommentSourceFlag,
    } from "../commentSources";
    import type { CommentSourceFlags } from "../commentSources";
    import { getContext } from "svelte";
    import type { Metadata } from "../types";
    import { CommentStyle, commentStyleStore, setCommentStyle } from "../commentStyles";

    let commentSourceFlags: CommentSourceFlags;
    commentSourceFlagsStore.subscribe((v) => {
        commentSourceFlags = v;
    });

    let commentStyle: CommentStyle;
    commentStyleStore.subscribe((v) => {commentStyle = v;})

    function setCommentStyleFromEvent(e) {
        setCommentStyle(e.target.value);
    }

    const metadata: Metadata = getContext("metadata");

    export let homeButton: boolean = false;

    const backgroundColor = "#dddddd";

    let commentSettingsFolded = true;
    function toggleCommentSettingsFolded(e) {
        commentSettingsFolded = !commentSettingsFolded;
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
        <div id="commentSettings" class={commentSettingsFolded ? "folded" : ""}>
            <div class="settings-block">
                <h4>Авторы</h4>
                {#each Object.entries(commentSourceFlags) as [commenter, isActive]}
                    <input
                        type="checkbox"
                        id={commenter}
                        name={commenter}
                        checked={isActive}
                        on:change={(e) => {
                            toggleCommentSourceFlag(commenter);
                        }}
                    />
                    <label for={commenter}
                        >{metadata.commenter_names[commenter]}</label
                    ><br />
                {/each}
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
            <div class="settings-block">
                <h4>Стиль</h4>
                {#each Object.values(CommentStyle) as style}
                    {#if style == CommentStyle.ASTRERISK}
                        <input
                            type="radio"
                            id={style}
                            name="commentStyle"
                            value={style}
                            checked={commentStyle == CommentStyle.ASTRERISK}
                            on:change={setCommentStyleFromEvent}
                        />
                        <label for={style}>
                            <span>Окно, звёздочки</span>
                            <InlineIcon heightEm={0.7}>
                                <Icon icon={"asterisk"} color={"#606060"} />
                            </InlineIcon>
                        </label>
                    {:else if style == CommentStyle.CLICKABLE_TEXT}
                        <input
                            type="radio"
                            id={style}
                            name="commentStyle"
                            value={style}
                            checked={commentStyle == CommentStyle.CLICKABLE_TEXT}
                            on:change={setCommentStyleFromEvent}
                        />
                        <label for={style}>
                            <span>Окно, <span class="clickable">нажимаемый текст</span></span>
                        </label>
                    {/if}
                    <br />
                {/each}
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
</style>
