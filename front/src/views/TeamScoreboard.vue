<template>
    <div id="app">
        <header>
            <topbar :round="round" />
        </header>
        <container>
            <statuses />
            <team-scoreboard :updateRound="updateRound" />
        </container>
        <footer class="footer">
            Powered by <span class="team">C4T BuT S4D</span> CTF team
        </footer>
    </div>
</template>

<script>
import Container from '@/components/Container/Index';
import Topbar from '@/components/Topbar/Index';
import TeamScoreboard from '@/components/TeamScoreboard/Index';
import Statuses from '@/components/Statuses/Index';

export default {
    components: {
        Container,
        Topbar,
        TeamScoreboard,
        Statuses,
    },

    data: function() {
        return {
            round: 0,
        };
    },

    methods: {
        updateRound: function(round) {
            this.round = round;
        },
    },
};
</script>

<style lang="scss" scoped>
#app {
    height: 100%;
    display: flex;

    flex-flow: column nowrap;

    & > :nth-child(2) {
        flex-grow: 1;
    }
}

.footer {
    text-align: center;
    margin-top: 3em;
}

.team {
    font-size: 1.1em;
}
</style>
