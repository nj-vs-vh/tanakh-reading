import Title from "./routes/Title.svelte";
import ParshaProvider from "./components/ParshaProvider.svelte";
import NotFound from "./routes/NotFound.svelte";
import Signup from "./routes/Signup.svelte";
import Login from "./routes/Login.svelte";
import Account from "./routes/Account.svelte";

import type { Route } from "svelte-router-spa/types/components/router";
import { parshaPath, signupPath } from "./utils";


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
        name: signupPath(":token"),
        component: Signup,
    },
    {
        name: "/login",
        component: Login,
    },
    {
        name: "/account",
        component: Account,
    },
    {
        name: "404",
        component: NotFound,
    }
]
