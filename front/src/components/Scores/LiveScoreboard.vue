<template>
    <div class="flag">
        <error-box :error="error">
            <div
                :key="index"
                v-for="({ attacker, victim, task, delta }, index) in events"
            >
                <span class="mark">{{ attacker }}</span> stole a flag from
                <span class="mark">{{ victim }}</span
                >'s service <span class="mark">{{ task }}</span> and got
                <span class="mark">{{ delta }}</span> points
            </div>
        </error-box>
    </div>
</template>

<script>
import { serverUrl } from '@/config';
import io from 'socket.io-client';
import ErrorBox from '@/components/Lib/ErrorBox';

export default {
    components: {
        ErrorBox,
    },

    data: function() {
        return {
            error: null,
            server: null,
            teams: null,
            tasks: null,
            events: [],
        };
    },

    created: async function() {
        try {
            const { data: teams } = await this.$http.get(
                `${serverUrl}/api/client/teams/`
            );
            const { data: tasks } = await this.$http.get(
                `${serverUrl}/api/client/tasks/`
            );
            this.teams = teams;
            this.tasks = tasks;
        } catch (e) {
            console.error('Fetching data:', e);
            this.error = "Can't connect to server";
            return;
        }

        this.server = io(`${serverUrl}/live_events`, {
            forceNew: true,
        });
        this.server.on('connect_error', error => {
            console.error(
                'Error connecting to socket.io server:',
                error.message
            );
            this.error = "Can't connect to server";
        });
        this.server.on('flag_stolen', ({ data }) => {
            this.error = null;
            const {
                attacker_id: attackerId,
                victim_id: victimId,
                task_id: taskId,
                attacker_delta: delta,
            } = data;

            this.events.unshift({
                attacker: this.teams.filter(({ id }) => id === attackerId)[0]
                    .name,
                victim: this.teams.filter(({ id }) => id === victimId)[0].name,
                task: this.tasks.filter(({ id }) => id == taskId)[0].name,
                delta,
            });
        });
    },
};
</script>

<style lang="scss" scoped>
.flag {
    color: #00ff00;
    background-color: black;
}

.mark {
    color: #ffff00;
}
</style>
