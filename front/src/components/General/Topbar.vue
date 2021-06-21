<template>
    <div class="topbar">
        <router-link class="tp" to="/live/" @click="go">Live</router-link>
        <div class="progress-bar" :style="{ width: roundProgressInteger }" />
        <div class="tp">Round: {{ round }}</div>
    </div>
</template>

<script>
export default {
    props: {
        round: Number,
        timer: Number,
        roundProgress: Number,
    },

    computed: {
        roundProgressInteger: function() {
            return `${Math.floor(this.roundProgress * 100)}%`;
        },
    },

    methods: {
        go: function() {
            clearInterval(this.timer);
        },
    },
};
</script>

<style lang="scss" scoped>
.tp {
    z-index: 1;
}

.topbar {
    position: relative;
    background: #bbbbbb55;
    padding: 1em;

    display: flex;
    flex-flow: row nowrap;

    justify-content: space-between;
    align-items: center;
}

.progress-bar {
    background-color: #00ff00;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    opacity: 0.5;
}
</style>
