<template>
    <div class="flag" v-if="error !== null">{{ error }}</div>
    <div class="flag" v-else>
        <div :key="index" v-for="({ attacker, victim, task, delta }, index) in events">
            <span class="mark">{{ attacker }}</span> stole a flag from
            <span class="mark">{{ victim }}</span>'s service
            <span class="mark">{{ task }}</span> and got
            <span class="mark">{{ delta }}</span> points
        </div>
    </div>
</template>

<script>
import { serverUrl } from '@/config';
import io from 'socket.io-client';

export default {
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
                `${serverUrl}/api/teams/`
            );
            const { data: tasks } = await this.$http.get(
                `${serverUrl}/api/tasks/`
            );
            this.teams = teams;
            this.tasks = tasks;
        } catch {
            this.error = "Can't connect to server";
            return;
        }

        this.server = io(`${serverUrl}/live_events`, {
            forceNew: true,
        });
        this.server.on('connect_error', () => {
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
