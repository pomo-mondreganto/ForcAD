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
            <div class="create-group">
                <button class="create-btn" @click="createTask">
                    Create task
                </button>
                <button class="create-btn" @click="createTeam">
                    Create team
                </button>
            </div>
            <admin-scoreboard
                :updateRound="updateRound"
                :updateRoundStart="updateRoundStart"
                :timer="timer"
            />
        </container>
        <footer class="footer">
            Powered by
            <span class="team">C4T BuT S4D</span> CTF team
        </footer>
    </div>
</template>

<script>
import Container from '@/components/Container/Index';
import Topbar from '@/components/Topbar/Index';
import AdminScoreboard from '@/components/AdminScoreboard/Index';
import axios from 'axios';
import { serverUrl } from '@/config';

export default {
    components: {
        Container,
        Topbar,
        AdminScoreboard,
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
        const r = await axios.get(`${serverUrl}/api/client/config/`);
        const { round_time } = r.data;
        this.roundTime = round_time;
        this.timer = setInterval(this.tick, 500);
    },

    methods: {
        updateRound: function(round) {
            this.round = round;
        },

        updateRoundStart: function(roundStart) {
            this.roundStart = roundStart;
        },

        createTask: async function() {
            this.$router.push({ name: 'createTask' }).catch(() => {});
        },

        createTeam: async function() {
            this.$router.push({ name: 'createTeam' }).catch(() => {});
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

.create-group {
    display: flex;
    flex-flow: row-reverse;
}

.create-btn {
    font-size: 1em;
    margin: 1em;
}

.footer {
    text-align: center;
    margin-top: 3em;
}

.team {
    font-size: 1.1em;
}
</style>
