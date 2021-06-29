<template>
    <div id="app">
        <header>
            <topbar />
        </header>
        <container>
            <slot />
        </container>
        <footer class="footer">
            Powered by
            <span class="team">C4T BuT S4D</span> CTF team
        </footer>
    </div>
</template>

<script>
import Container from '@/components/Lib/Container';
import Topbar from '@/components/General/Topbar';
import io from 'socket.io-client';
import { serverUrl } from '@/config';

export default {
    components: {
        Container,
        Topbar,
    },

    data: function() {
        return {
            server: null,
        };
    },

    created: async function() {
        this.server = io(`${serverUrl}/game_events`, {
            forceNew: true,
        });
        this.server.on('connect_error', () => {
            this.error = "Can't connect to server";
        });
        this.server.on('init_scoreboard', ({ data }) => {
            this.error = null;
            this.$store.dispatch('handleInitScoreboardMessage', data);
        });
        this.server.on('update_scoreboard', ({ data }) => {
            this.error = null;
            this.$store.dispatch('handleUpdateScoreboardMessage', data);
        });
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
</style>
