<script lang="ts">
    export let color: string = "grey";
    export let icon:
        | "asterisk"
        | "synagogue"
        | "comment"
        | "chevron-left"
        | "chevron-right"
        | "torah-scroll";
</script>

{#if icon == "asterisk"}
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 512 512"
        stroke={color}
        fill={color}
        ><!--! Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path
            d="M208 32c0-17.7 14.3-32 32-32h32c17.7 0 32 14.3 32 32V172.9l122-70.4c15.3-8.8 34.9-3.6 43.7 11.7l16 27.7c8.8 15.3 3.6 34.9-11.7 43.7L352 256l122 70.4c15.3 8.8 20.5 28.4 11.7 43.7l-16 27.7c-8.8 15.3-28.4 20.6-43.7 11.7L304 339.1V480c0 17.7-14.3 32-32 32H240c-17.7 0-32-14.3-32-32V339.1L86 409.6c-15.3 8.8-34.9 3.6-43.7-11.7l-16-27.7c-8.8-15.3-3.6-34.9 11.7-43.7L160 256 38 185.6c-15.3-8.8-20.5-28.4-11.7-43.7l16-27.7C51.1 98.8 70.7 93.6 86 102.4l122 70.4V32z"
        /></svg
    >
{:else if icon == "synagogue"}
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 640 512"
        stroke={color}
        fill={color}
        ><!--! Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path
            d="M309.8 3.7c5.9-4.9 14.6-4.9 20.5 0l121 100.8C469.5 119.7 480 142.2 480 166V280.1 512H464 352V416c0-17.7-14.3-32-32-32s-32 14.3-32 32v96H176 160V280.1 166c0-23.7 10.5-46.3 28.8-61.5L309.8 3.7zM512 512V244.5l28.1-31.2c3-3.4 7.4-5.3 11.9-5.3s8.9 1.9 11.9 5.3l63.8 70.9c7.9 8.8 12.3 20.3 12.3 32.1V448c0 35.3-28.7 64-64 64H512zM128 244.5V512H64c-35.3 0-64-28.7-64-64V316.3c0-11.9 4.4-23.3 12.3-32.1l63.8-70.9c3-3.4 7.4-5.3 11.9-5.3s8.9 1.9 11.9 5.3L128 244.5zM327 124.3c-3.1-5.4-10.9-5.4-13.9 0l-15.9 28.1-32.3-.3c-6.2-.1-10.1 6.7-7 12.1L274.3 192l-16.4 27.8c-3.2 5.4 .7 12.1 7 12.1l32.3-.3L313 259.7c3.1 5.4 10.9 5.4 13.9 0l15.9-28.1 32.3 .3c6.2 .1 10.1-6.7 7-12.1L365.7 192l16.4-27.8c3.2-5.4-.7-12.1-7-12.1l-32.3 .3L327 124.3z"
        /></svg
    >
{:else if icon == "comment"}
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 512 512"
        stroke={color}
        fill={color}
        ><!--! Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path
            d="M512 240c0 114.9-114.6 208-256 208c-37.1 0-72.3-6.4-104.1-17.9c-11.9 8.7-31.3 20.6-54.3 30.6C73.6 471.1 44.7 480 16 480c-6.5 0-12.3-3.9-14.8-9.9c-2.5-6-1.1-12.8 3.4-17.4l0 0 0 0 0 0 0 0 .3-.3c.3-.3 .7-.7 1.3-1.4c1.1-1.2 2.8-3.1 4.9-5.7c4.1-5 9.6-12.4 15.2-21.6c10-16.6 19.5-38.4 21.4-62.9C17.7 326.8 0 285.1 0 240C0 125.1 114.6 32 256 32s256 93.1 256 208z"
        /></svg
    >
{:else if icon == "chevron-left"}
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 384 512"
        stroke={color}
        fill={color}
        ><!--! Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path
            d="M41.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l192 192c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L109.3 256 278.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-192 192z"
        /></svg
    >
{:else if icon == "chevron-right"}
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 384 512"
        stroke={color}
        fill={color}
        ><!--! Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path
            d="M342.6 233.4c12.5 12.5 12.5 32.8 0 45.3l-192 192c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L274.7 256 105.4 86.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l192 192z"
        /></svg
    >
{:else if icon == "torah-scroll"}
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 640 512"
        stroke={color}
        fill={color}
        ><!--! Font Awesome Pro 6.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path
            d="M96 480V32C96 14.3 74.5 0 48 0S0 14.3 0 32V480c0 17.7 21.5 32 48 32s48-14.3 48-32zM512 32H128V480H512V32zM592 0c-26.5 0-48 14.3-48 32V480c0 17.7 21.5 32 48 32s48-14.3 48-32V32c0-17.7-21.5-32-48-32zM196 313.7c0-3.2 .9-6.4 2.5-9.2L226.7 256l-28.3-48.5c-1.6-2.8-2.5-6-2.5-9.2c0-10.1 8.2-18.3 18.3-18.3H271l31.4-53.9c3.6-6.3 10.3-10.1 17.6-10.1s13.9 3.8 17.6 10.1L369 180h56.7c10.1 0 18.3 8.2 18.3 18.3c0 3.2-.9 6.4-2.5 9.2L413.3 256l28.3 48.5c1.6 2.8 2.5 6 2.5 9.2c0 10.1-8.2 18.3-18.3 18.3H369l-31.4 53.9c-3.6 6.3-10.3 10.1-17.6 10.1s-13.9-3.8-17.6-10.1L271 332H214.3c-10.1 0-18.3-8.2-18.3-18.3zm124 54.7L341.2 332H298.8L320 368.4zM254.5 256l30.3 52h70.4l30.3-52-30.3-52H284.8l-30.3 52zm144.9 23.8L383 308h32.8l-16.4-28.2zM415.8 204H383l16.4 28.2L415.8 204zM320 143.6L298.8 180h42.4L320 143.6zM224.2 204l16.4 28.2L257 204H224.2zM257 308l-16.4-28.2L224.2 308H257z"
        /></svg
    >
{/if}
