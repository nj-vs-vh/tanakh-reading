import type { SingleComment, SingleText } from "../../types";

export type Entity = SingleComment | SingleText;

export function getText(entity: Entity): string {
    // @ts-ignore
    if (entity.index !== undefined) {
        // @ts-ignore
        return entity.comment;
    } else {
        // @ts-ignore
        return entity.text;
    }
}
export function withText(entity: Entity, newText: string): Entity {
    const copy = { ...entity };
    // @ts-ignore
    if (entity.index !== undefined) {
        // @ts-ignore
        copy.comment = newText;
    } else {
        // @ts-ignore
        copy.text = newText;
    }
    return copy;
}
