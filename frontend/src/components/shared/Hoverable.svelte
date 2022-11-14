<script lang="ts">
    export let isHovering = false;
    function setHovering() {
        isHovering = true;
    }
    function unsetHovering() {
        isHovering = false;
    }
</script>

<div on:mouseover={setHovering} on:mouseout={unsetHovering} on:focus={setHovering} on:blur={unsetHovering}>
    <slot />
</div>
