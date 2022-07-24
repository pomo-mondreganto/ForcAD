<template>
    <div>
        <p v-if="error !== null" class="error-message">
            {{ error }}
        </p>
        <slot v-else />
    </div>
</template>

<script>
export default {
    props: {
        error: {
            validator: (prop) => typeof prop === 'string' || prop === null,
            required: true,
        },
    },
};
</script>

<style lang="scss" scoped>
.error-message {
    color: red;
}
</style>
