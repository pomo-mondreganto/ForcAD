<template>
    <error-box :error="error">
        <score-table
            v-if="teams !== null"
            headRowTitle="#"
            @openTeam="openTeam"
            @openTask="openTask"
            @openTeamAdmin="openTeamAdmin"
            @openTaskAdmin="openTaskAdmin"
            @openTeamTaskHistory="openTeamTaskHistory"
            :teamClickable="true"
            :admin="true"
            :tasks="tasks"
            :teams="teams"
        />
    </error-box>
</template>

<script>
import io from 'socket.io-client';
import { serverUrl } from '@/config';
import Task from '@/models/task';
import Team from '@/models/team';
import ScoreTable from '@/components/Lib/ScoreTable';
import ErrorBox from '@/components/Lib/ErrorBox';

export default {
    components: {
        ScoreTable,
        ErrorBox,
    },

    props: {
        updateRound: Function,
        updateRoundStart: Function,
        timer: Number,
    },

    data: function() {
        return {
            error: null,
            server: null,
            tasks: null,
            teams: null,
            round_start: 0,
        };
    },

    methods: {
        openTeam: function(id) {
            clearInterval(this.timer);
            this.$router.push({ name: 'team', params: { id } }).catch(() => {});
        },
        openTaskAdmin: function(id) {
            clearInterval(this.timer);
            this.$router
                .push({ name: 'taskAdmin', params: { id } })
                .catch(() => {});
        },
        openTeamAdmin: function(id) {
            clearInterval(this.timer);
            this.$router
                .push({ name: 'teamAdmin', params: { id } })
                .catch(() => {});
        },
        openTeamTaskHistory: function(teamId, taskId) {
            clearInterval(this.timer);
            this.$router
                .push({
                    name: 'adminTeamTaskLog',
                    params: { teamId: teamId, taskId: taskId },
                })
                .catch(() => {});
        },
    },

    created: function() {
        this.server = io(`${serverUrl}/game_events`, {
            forceNew: true,
        });
        this.server.on('connect_error', () => {
            this.error = "Can't connect to server";
        });
        this.server.on('init_scoreboard', async ({ data }) => {
            this.error = null;
            const {
                state: { round_start, round, team_tasks: teamTasks },
            } = data;

            const { data: tasks } = await this.$http.get('/admin/tasks/');
            const { data: teams } = await this.$http.get('/admin/teams/');

            this.updateRoundStart(round_start);
            this.updateRound(round);
            this.tasks = tasks.map(task => new Task(task)).sort(Task.comp);
            this.teams = teams
                .map(
                    team =>
                        new Team({
                            ...team,
                            tasks: this.tasks,
                            teamTasks,
                        })
                )
                .sort(Team.comp);
        });
        this.server.on('update_scoreboard', ({ data }) => {
            this.error = null;
            const { round, team_tasks: teamTasks, round_start } = data;
            this.updateRoundStart(round_start);
            this.updateRound(round);
            this.teams.forEach(team => {
                team.update(teamTasks);
            });
            this.teams = this.teams.sort(Team.comp);
        });
    },
};
</script>

<style lang="scss" scoped></style>
