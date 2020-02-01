<template>
    <div v-if="error !== null">
        {{ error }}
    </div>
    <div v-else-if="team !== null" class="table">
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
        <div>
            <div class="row" v-for="state in states" :key="state.tasks[0].id">
                <div class="number">
                    {{ state.tasks[0].round }}
                </div>
                <div class="team">
                    <div class="team-name">{{ team.name }}</div>
                    <div class="ip">{{ team.ip }}</div>
                </div>
                <div class="score">
                    {{ state.score.toFixed(2) }}
                </div>
                <div class="service">
                    <div
                        v-for="{
                            id,
                            up_rounds: upRounds,
                            round,
                            score,
                            stolen,
                            lost,
                            message,
                            status,
                        } in state.tasks"
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
                            <strong>SLA</strong>:
                            {{
                                (
                                    (100.0 * upRounds) /
                                    Math.max(round, 1)
                                ).toFixed(2)
                            }}%
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
        </div>
    </div>
</template>

<script>
import { serverUrl } from '@/config';

export default {
    props: {
        updateRound: Function,
    },

    data: function() {
        return {
            error: null,
            team: null,
            teamId: null,
            tasks: null,
            round: 0,
        };
    },

    created: async function() {
        this.teamId = this.$route.params.id;
        try {
            const { data: teams } = await this.$http.get(
                `${serverUrl}/api/teams/`
            );
            const { data: tasks } = await this.$http.get(
                `${serverUrl}/api/tasks/`
            );
            const { data: states } = await this.$http.get(
                `${serverUrl}/api/teams/${this.teamId}`
            );
            this.team = teams.filter(({ id }) => id == this.teamId)[0];
            this.tasks = tasks.sort(({ id: idA }, { id: idB }) => idA - idB);
            this.round = states.reduce(
                (acc, { round }) => Math.max(acc, round),
                0
            );
            this.updateRound(this.round);
            this.states = [];
            for (let i = this.round; i >= 0; i -= 1) {
                this.states.push({
                    tasks: states
                        .filter(({ round }) => round === i)
                        .sort(
                            ({ task_id: taskIdA }, { task_id: taskIdB }) =>
                                taskIdA - taskIdB
                        ),
                    score: states
                        .filter(({ round }) => round === i)
                        .reduce(
                            (acc, { score, upRounds, round }) =>
                                acc + score * (upRounds / Math.max(round, 1)),
                            0
                        ),
                });
            }

            this.states = this.states.filter(
                state => state.tasks.length == this.states[0].tasks.length
            );
        } catch {
            this.error = "Can't connect to server";
        }
    },
};
</script>

<style lang="scss" scoped>
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
