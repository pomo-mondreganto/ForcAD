<template>
    <div id="app">
        <header>
            <topbar
                :round="round"
                :roundProgress="roundProgress"
                :timer="timer"
            />
        </header>
        <container>
            <statuses />
            <scoreboard
                :updateRound="updateRound"
                :updateRoundStart="updateRoundStart"
                :timer="timer"
            />
        </container>
        <footer class="footer">
            Powered by <span class="team">C4T BuT S4D</span> CTF team
        </footer>
    </div>
</template>

<script>
import Container from '@/components/Container/Index';
import Topbar from '@/components/Topbar/Index';
import Scoreboard from '@/components/Scoreboard/Index';
import Statuses from '@/components/Statuses/Index';
import axios from 'axios';
import { serverUrl } from '@/config';

export default {
    components: {
        Container,
        Topbar,
        Scoreboard,
        Statuses,
    },

    data: function() {
        return {
            round: 0,
            roundStart: 0,
            timer: null,
            roundTime: null,
            roundProgress: null,
        };
    },

    created: async function() {
        const r = await axios.get(`${serverUrl}/api/config`);
        const { round_time } = r.data;
        this.roundTime = round_time;
        this.timer = setInterval(this.tick, 1000);
    },

    methods: {
        updateRound: function(round) {
            this.round = round;
        },

        updateRoundStart: function(roundStart) {
            this.roundStart = roundStart;
        },

        tick: function() {
            if (
                this.roundTime === null ||
                this.roundStart === null ||
                this.round < 1
            ) {
                this.roundProgress = 0;
            } else {
                this.roundProgress =
                    (new Date().getTime() / 1000 -
                        this.roundStart -
                        this.roundTime) /
                    this.roundTime;
                this.roundProgress = Math.min(this.roundProgress, 1);
            }
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
