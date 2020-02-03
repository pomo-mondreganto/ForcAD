<template>
    <div class="topbar">
        <router-link to="/live/">Live</router-link>
        <div>Round: {{ round }}</div>
    </div>
</template>

<script>
export default {
    props: {
        round: Number,
    },
};
</script>

<style lang="scss" scoped>
.topbar {
    background: #bbbbbb55;
    padding: 1em;

    display: flex;
    flex-flow: row nowrap;

    justify-content: space-between;
}
</style>
