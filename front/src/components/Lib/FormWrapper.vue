<template>
    <form @submit.prevent="handleSubmit">
        <p>{{ title }}</p>
        <slot />
        <p v-if="error !== null" class="error-message">{{ error }}</p>
        <input type="submit" value="Submit" />
    </form>
</template>

<script>
export default {
    props: {
        title: String,
        submitCallback: Function,
    },

    data: function() {
        return {
            error: null,
        };
    },

    methods: {
        handleSubmit: async function() {
            try {
                await this.submitCallback();
            } catch (e) {
                console.error(e);
                this.error = e;
            }
        },
    },
};
</script>

<style lang="scss" scoped>
.error-message {
    color: red;
}
</style>
