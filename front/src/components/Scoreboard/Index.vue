<template>
    <div v-if="error !== null">
        {{ error }}
    </div>
    <div v-else-if="teams !== null" class="table">
        <div class="row">
            <div class="number">#</div>
            <div class="team">team</div>
            <div class="score">score</div>
            <div class="service-name">
                <div v-for="{ name } in tasks" :key="name" class="service-cell">
                    {{ name }}
                </div>
            </div>
        </div>
        <transition-group name="teams-list">
            <div
                class="row"
                v-for="({ name, score, tasks, ip }, index) in teams"
                :key="name"
            >
                <div class="number" :class="`top-${index + 1}`">
                    {{ index + 1 }}
                </div>
                <div class="team" :class="`top-${index + 1}`">
                    <div class="team-name">{{ name }}</div>
                    <div class="ip">{{ ip }}</div>
                </div>
                <div class="score" :class="`top-${index + 1}`">
                    {{ score.toFixed(2) }}
                </div>
                <div class="service">
                    <div
                        v-for="{
                            id,
                            sla,
                            score,
                            stolen,
                            lost,
                            message,
                            status,
                        } in tasks"
                        :key="id"
                        class="service-cell"
                        :class="`status-${status}`"
                    >
                        <button class="info">
                            <i class="fas fa-info-circle" />
                            <span class="tooltip">
                                {{ message === '' ? 'OK' : message }}
                            </span>
                        </button>
                        <div class="sla">
                            <strong>SLA</strong>: {{ sla.toFixed(2) }}%
                        </div>
                        <div class="fp">
                            <strong>FP</strong>: {{ score.toFixed(2) }}
                        </div>
                        <div class="flags">
                            <i class="fas fa-flag" /> +{{ stolen }}/-{{ lost }}
                        </div>
                    </div>
                </div>
            </div>
        </transition-group>
    </div>
</template>

<script>
import io from 'socket.io-client';
import { serverUrl } from '@/config';
import Task from '@/models/task';
import Team from '@/models/team';

export default {
    props: {
        updateRound: Function,
    },

    data: function() {
        return {
            error: null,
            server: null,
            tasks: null,
            teams: null,
        };
    },

    created: function() {
        this.server = io(`${serverUrl}/api/sio_interface`, {
            forceNew: true,
        });
        this.server.on('connect_error', () => {
            this.error = "Can't connect to server";
        });
        this.server.on('init_scoreboard', ({ data }) => {
            this.error = null;
            const {
                state: { round, team_tasks: teamTasks },
                tasks,
                teams,
            } = JSON.parse(data);

            this.updateRound(round);
            this.tasks = tasks.map(task => new Task(task)).sort(Task.comp);
            this.teams = teams
                .map(
                    team =>
                        new Team({
                            ...team,
                            teamTasks,
                        })
                )
                .sort(Team.comp);
        });
        this.server.on('update_scoreboard', ({ data }) => {
            this.error = null;
            const { round, team_tasks: teamTasks } = JSON.parse(data);
            this.updateRound(round);
            this.teams.forEach(team => {
                team.update(teamTasks);
            });
            this.teams = this.teams.sort(Team.comp);
        });
    },
};
</script>

<style lang="scss" scoped>
.teams-list-move {
    transition: transform 1s;
}

.table {
    display: flex;
    flex-flow: column nowrap;

    & > :first-child > :not(:last-child) {
        font-weight: bold;
        padding-top: 0.6em;
        padding-bottom: 0.6em;
    }

    & > :not(:first-child) > * {
        height: 6em;
    }

    & > :last-child > :last-child > * {
        border-bottom: 1px solid #c6cad1;
    }
}

.row {
    display: flex;
    flex-flow: row nowrap;
    text-align: center;

    & > * {
        border-top: 1px solid #c6cad1;
        word-wrap: break-word;
        min-width: 0;
    }

    & > :first-child {
        border-left: 1px solid #c6cad1;
    }

    & > :last-child {
        border-right: 1px solid #c6cad1;
    }
}

.team-name {
    font-weight: bold;
}

.number {
    flex: 1 1 0;
    display: flex;
    flex-flow: column nowrap;
    justify-content: center;
}

.team {
    flex: 4 1 15%;
    display: flex;
    flex-flow: column nowrap;
    justify-content: center;
}

.score {
    flex: 2 1 5%;
    display: flex;
    flex-flow: column nowrap;
    justify-content: center;
}

.service {
    flex: 20 2 0;
    display: flex;
    flex-flow: row nowrap;

    border-left: 1px solid #c6cad1;

    & > :not(:last-child) {
        border-right: 1px solid #c6cad1;
    }
}

.service-name {
    flex: 20 2 0;
    display: flex;
    flex-flow: row nowrap;
    text-align: center;
}

.service-cell {
    flex: 1 1 0;

    position: relative;

    display: flex;
    flex-flow: column nowrap;
    justify-content: space-around;
}

.sla {
    text-align: left;
    margin-left: 0.5em;
}

.fp {
    text-align: left;
    margin-left: 0.5em;
}

.flags {
    text-align: left;
    margin-left: 0.5em;
}

.info {
    position: absolute;
    top: 0.5em;
    left: calc(100% - 2.5em - 0.5em);
    width: 2.5em;
    height: 2.5em;

    border-radius: 0.3em;
    font-size: 0.7em;
    border: 1px solid #c6cad1;

    &:focus {
        outline: 0;
        border: 1px solid #c6cad1;
    }
}

.tooltip {
    left: 0;
    top: 0;
    transform: translateX(calc(-100%)) translateY(calc(-100% - 0.25em));
    position: absolute;
    width: 20em;
    text-align: center;
    display: block;
    background-color: black;
    color: white;
    border-radius: 0.5em;
    padding: 1em;
    opacity: 0;
    z-index: -1;
}

.info:hover .tooltip {
    opacity: 1;
    z-index: 1;
}
</style>
