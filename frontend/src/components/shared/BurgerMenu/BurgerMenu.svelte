<script lang="ts">
    import BurgerButton from "./BurgerButton.svelte";
    import SideMenu from "./SideMenu.svelte";

    export let open: boolean = false;

    export let duration: number = 0.4;
    export let width: string = "300px";
    export let padding: string = "25px";
    export let paddingTop: string = "50px";
    export let backgroundColor: string;
    export let burgerColor: string;
    export let menuColor: string;

    let burgerProps = {
        duration: duration,
        burgerColor: burgerColor,
        menuColor: menuColor,
    };

    let menuProps = {
        duration: duration,
        width: width,
        padding: padding,
        paddingTop: paddingTop,
        backgroundColor: backgroundColor,
        menuColor: menuColor,
    };
</script>

<BurgerButton {...burgerProps} bind:open />

<SideMenu {...menuProps} bind:open>
    <slot />
</SideMenu>
