<template>
    <div class="topbar">
        <router-link class="tp" to="/live/">Live</router-link>
        <div class="progress-bar" :style="{ width: `${roundProgress}%` }" />
        <div class="tp">Round: {{ round }}</div>
    </div>
</template>

<script>
import { mapState } from 'vuex';
export default {
    data: function() {
        return {
            timer: null,
        };
    },

    created: async function() {
        await this.$store.dispatch('fetchRoundTime');
        this.timer = setInterval(
            () => this.$store.dispatch('calculateRoundProgress'),
            500
        );
    },

    beforeRouteLeave: function(to, from, next) {
        clearInterval(this.timer);
        next();
    },

    computed: mapState(['round', 'roundProgress']),
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
