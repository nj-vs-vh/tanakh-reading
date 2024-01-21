<script lang="ts">
    export let isHovering = false;
    export let inertiaMs = 500;

    let isHoveringImmediate = isHovering;
    function setHovering() {
        isHovering = true;
        isHoveringImmediate = true;
    }
    function unsetHovering() {
        isHoveringImmediate = false;
        // smoothing out on-off "flickering" on fast mouse movements
        setTimeout(() => {
            if (isHovering && !isHoveringImmediate) {
                isHovering = false;
                isHoveringImmediate = false;
            }
        }, inertiaMs);
    }
</script>

<div on:mouseover={setHovering} on:mouseout={unsetHovering} on:focus={setHovering} on:blur={unsetHovering}>
    <slot />
</div>
