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
            <div class="row" v-for="(state, index) in states" :key="index">
                <div class="number">
                    {{ state.tasks[0].checks }}
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
                            checks,
                            checks_passed: checksPassed,
                            score,
                            stolen,
                            lost,
                            message,
                            status,
                        } in state.tasks"
                        :key="id"
                        class="service-cell"
                        :style="{
                            'font-size': `${1 - tasks.length / 20}em`,
                        }"
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
                                    (100.0 * checksPassed) /
                                    Math.max(checks, 1)
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
        updateRoundStart: Function,
    },

    data: function() {
        return {
            error: null,
            team: null,
            teamId: null,
            tasks: null,
            round: 0,
            by_task: [],
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
            let { data: states } = await this.$http.get(
                `${serverUrl}/api/teams/${this.teamId}`
            );
            this.team = teams.filter(({ id }) => id == this.teamId)[0];
            this.tasks = tasks.sort(({ id: idA }, { id: idB }) => idA - idB);

            this.round = states.reduce(
                (acc, { round }) => Math.max(acc, round),
                0
            );

            this.updateRound(this.round);

            states = states.map(x => ({
                id: Number(x.id),
                round: Number(x.round),
                task_id: Number(x.task_id),
                team_id: Number(x.team_id),
                status: x.status,
                stolen: x.stolen,
                lost: x.lost,
                score: Number(x.score),
                checks: Number(x.checks),
                checks_passed: Number(x.checks_passed),
                timestamp_secs: Number(
                    x.timestamp.slice(0, x.timestamp.indexOf('-'))
                ),
                timestamp_num: Number(
                    x.timestamp.slice(x.timestamp.indexOf('-') + 1)
                ),
                message: x.message,
            }));

            states = states.sort(
                (
                    { timestamp_secs: tss1, timestamp_num: tsn1 },
                    { timestamp_secs: tss2, timestamp_num: tsn2 }
                ) => {
                    if (tss1 === tss2) {
                        return tsn2 - tsn1;
                    }
                    return tss2 - tss1;
                }
            );

            this.by_task = tasks.map(() => []);
            for (const state of states) {
                this.by_task[state.task_id - 1].push(state);
            }

            let row_count = Math.min(...this.by_task.map(x => x.length));

            this.states = [];
            for (let i = 0; i < row_count; i += 1) {
                this.states.push({
                    tasks: this.by_task.map(x => x[i]),
                    score: this.by_task
                        .map(x => x[i])
                        .reduce(
                            (
                                acc,
                                { score, checks, checks_passed: checksPassed }
                            ) =>
                                acc +
                                score * (checksPassed / Math.max(checks, 1)),
                            0
                        ),
                });
            }
        } catch (e) {
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
    padding: 0;
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
    font-size: 0.7rem;
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
