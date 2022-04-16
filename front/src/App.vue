<template>
    <component :is="layout">
        <router-view />
    </component>
</template>

<script>
export default {
    computed: {
        layout() {
            return this.$route.meta.layout || 'default-layout';
        },
    },
};
</script>

<style lang="scss">
html,
body {
    height: 100%;
    margin: 0;
    background-color: white;
}

body {
    font-family: Merriweather, serif;
}
</style>
