import Title from "./components/Title.svelte";
import ParshaProvider from "./components/ParshaProvider.svelte";
import NotFound from "./components/NotFound.svelte";

import type { Route } from "svelte-router-spa/types/components/router";
import { parshaPath } from "./utils";


export const routes: Route[] = [
    {
        name: "/",
        component: Title,
    },
    {
        name: parshaPath(":parshaIndex"),
        component: ParshaProvider,
    },
    {
        name: "404",
        component: NotFound,
    }
]
