<template>
    <div class="topbar">
        <router-link to="/live/" @click="go">Live</router-link>
        <div class="progress-bar">
            <div
                class="progress-bar-progress"
                :style="{ width: roundProgressInteger, visibility: visible }"
            ></div>
        </div>
        <div>Round: {{ round }}</div>
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

        visible: function() {
            return this.roundProgress < 0.05 ? 'hidden' : 'visible';
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
.topbar {
    background: #bbbbbb55;
    padding: 1em;

    display: flex;
    flex-flow: row nowrap;

    justify-content: space-between;
    align-items: center;
}

.progress-bar {
    border: 1px solid #838383;
    border-radius: 10px;
    height: 7px;
    width: 70%;
    margin: 0;
}

.progress-bar-progress {
    background-color: #838383;
    border: 1px solid #838383;
    border-radius: 10px;
    height: 7px;
    margin: 0;
    margin-top: -1px;
    margin-left: -1px;
}
</style>
