<script lang="ts">
    import Screen from "../shared/Screen.svelte";
    import type { TextOrCommentIterRequest } from "../../types";

    import { RegexColorizer } from "./regexColorizing";
    import { iterComments, iterTexts } from "../../api";
    import { Entity, getText, withText } from "./utils";

    let target: "texts" | "comments" = "comments";

    let currentRequest: TextOrCommentIterRequest = {
        position: {
            parsha: null,
            chapter: null,
            verse: null,
        },
        source: null,
        offset: 0,
    };
    let currentEntity: Entity | null = null;
    let editedEntity: Entity | null = null;

    let regexFind: string = "";
    let regexColorizedHtml: string = "";
    let regexReplace: string = "";

    async function next() {
        const iterFunc = target === "comments" ? iterComments : iterTexts;
        while (true) {
            let newEntity: Entity;
            try {
                newEntity = await iterFunc(currentRequest);
            } catch {
                console.log("Iteration ended");
                break;
            }
            currentRequest.offset += 1;
            let text = getText(newEntity);
            if (text.search(regexFind) !== -1) {
                let newText = text.replaceAll(regexFind, regexReplace);
                currentEntity = newEntity;
                editedEntity = withText(newEntity, newText);
                return;
            }
        }
    }
</script>

<Screen>
    <header>
        <span style="font-size: x-large;">
            Редактирование
            <select bind:value={target} style="font-size: large;">
                <option value="texts">текстов</option>
                <option value="comments">комментариев</option>
            </select>
        </span>
        <div>
            <span class="position-input">
                Парша
                <input class="small-num" bind:value={currentRequest.position.parsha} type="number" />
            </span>
            <span class="position-input">
                Глава
                <input class="small-num" bind:value={currentRequest.position.chapter} type="number" />
            </span>
            <span class="position-input">
                Стих
                <input class="small-num" bind:value={currentRequest.position.verse} type="number" />
            </span>
        </div>
        <div>
            Источник <input bind:value={currentRequest.source} />
        </div>
        <hr style="border-top: 1px solid black; width: 90%;" />
        <div class="split-screen">
            <div class="split-part left">
                <textarea
                    placeholder="регулярное выражение"
                    bind:value={regexFind}
                    on:input={(e) => {
                        // @ts-ignore
                        regexColorizedHtml = RegexColorizer.colorizeText(e.target.value);
                    }}
                />
                <span class="regex">{@html regexColorizedHtml}</span>
            </div>
            <div class="split-part right">
                <textarea placeholder="замена" bind:value={regexReplace} />
            </div>
        </div>
        <div class="split-screen">
            <div class="split-part left">
                <div class="control-btn-container" style="justify-content: flex-end;">
                    <button on:click={next}>Дальше</button>
                </div>
            </div>
            <div class="split-part right">
                <div class="control-btn-container">
                    <button>Заменить</button>
                </div>
            </div>
        </div>
    </header>
    <div class="split-screen">
        <div class="split-part left" style="border-right: 1px solid black;">
            {#if currentEntity !== null}
                {getText(currentEntity)}
            {/if}
        </div>
        <div class="split-part right">
            {#if editedEntity !== null}
                {getText(editedEntity)}
            {/if}
        </div>
    </div>
</Screen>

<style>
    header {
        width: 100%;
        background-color: var(--theme-color-secondary-background);
        padding: 1em;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.6em;
    }

    div.split-screen {
        flex-grow: 1;
        width: min(100%, 900px);
        display: flex;
        flex-direction: row;
    }

    div.split-part {
        width: 50%;
        padding: 0 0.5em;
    }

    span.position-input {
        margin: 0 0.6em;
    }

    input {
        margin-left: 0.2em;
    }

    input.small-num {
        max-width: 3em;
    }
    textarea {
        width: 98.5%;
        resize: vertical;
    }
    div.control-btn-container {
        width: 100%;
        display: flex;
        flex-direction: row;
    }
    div.control-btn-container > button {
        font-size: larger;
        cursor: pointer;
    }
</style>
