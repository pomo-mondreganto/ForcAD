<template>
    <div class="topbar">Round: {{ round }}</div>
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
    text-align: right;
}
</style>
