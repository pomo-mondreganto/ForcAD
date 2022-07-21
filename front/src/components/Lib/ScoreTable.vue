<template>
    <div class="table">
        <div class="row">
            <div class="number">
                {{ headRowTitle }}
            </div>
            <div class="team">team 123</div>
            <div class="score">score</div>
            <div class="service-name">
                <div
                    v-for="{ name, id } in tasks"
                    :key="name"
                    :style="taskStyle"
                    class="service-cell"
                    @click="$emit('openTask', id)"
                >
                    {{ name }}
                    <button
                        v-if="admin"
                        class="edit"
                        @click="$emit('openTaskAdmin', id)"
                    >
                        <i class="fas fa-edit" />
                    </button>
                </div>
            </div>
        </div>
        <transition-group name="teams-list">
            <div
                v-for="(
                    {
                        name,
                        score: totalScore,
                        tasks: teamTasks,
                        ip,
                        id,
                        highlighted,
                    },
                    index
                ) in teams"
                :key="name"
                class="row"
                :class="[highlighted ? 'highlighted' : '']"
                :style="{
                    backgroundColor: getTeamRowBackground(index),
                }"
            >
                <div class="team-group" :class="highlighted ? '' : 'pd-3'">
                    <div
                        class="number"
                        :style="{
                            backgroundColor: getTeamRowBackground(index),
                        }"
                    >
                        {{ index + 1 }}
                    </div>
                    <div
                        class="team team-row"
                        :style="[
                            teamStyle,
                            { backgroundColor: getTeamRowBackground(index) },
                        ]"
                        @click="$emit('openTeam', id)"
                    >
                        <div class="team-name">
                            {{ name }}
                        </div>
                        <div class="ip">
                            {{ ip }}
                        </div>
                        <button
                            v-if="admin"
                            class="edit"
                            @click="$emit('openTeamAdmin', id)"
                            @click.stop
                        >
                            <i class="fas fa-edit" />
                        </button>
                    </div>
                    <div
                        class="score"
                        :style="{
                            backgroundColor: getTeamRowBackground(index),
                        }"
                    >
                        {{ totalScore.toFixed(2) }}
                    </div>
                </div>
                <div class="service">
                    <div
                        v-for="{
                            id: teamTaskID,
                            teamId,
                            taskId,
                            sla,
                            score,
                            stolen,
                            lost,
                            message,
                            status,
                        } in teamTasks"
                        :key="teamTaskID"
                        class="service-cell"
                        :style="{
                            fontSize: `${1 - teamTasks.length / 20}em`,
                            backgroundColor: getTeamTaskBackground(status),
                        }"
                    >
                        <button
                            v-if="admin"
                            class="tt-edit"
                            @click="
                                $emit('openTeamTaskHistory', teamId, taskId)
                            "
                        >
                            <i class="fas fa-edit" />
                        </button>
                        <button class="info">
                            <i class="fas fa-info-circle" />
                            <span class="tooltip">{{ message }}</span>
                        </button>
                        <div class="sla">
                            <strong>SLA</strong>
                            : {{ sla.toFixed(2) }}%
                        </div>
                        <div class="fp">
                            <strong>FP</strong>
                            : {{ score.toFixed(2) }}
                        </div>
                        <div class="flags">
                            <i class="fas fa-flag" />
                            +{{ stolen }}/-{{ lost }}
                        </div>
                    </div>
                </div>
            </div>
        </transition-group>
    </div>
</template>

<script>
import { getTeamRowBackground, getTeamTaskBackground } from '@/utils/colors';
import '@/assets/table.scss';

export default {
    props: {
        headRowTitle: {
            type: String,
            default: '#',
        },
        tasks: {
            type: Array,
            required: true,
        },
        teams: {
            type: Array,
            required: true,
        },
        teamClickable: Boolean,
        taskClickable: Boolean,
        admin: Boolean,
    },

    data: function () {
        return {
            getTeamRowBackground,
            getTeamTaskBackground,
        };
    },

    computed: {
        teamStyle: function () {
            return this.teamClickable
                ? {
                      cursor: 'pointer',
                  }
                : {};
        },

        taskStyle: function () {
            return this.taskClickable
                ? {
                      cursor: 'pointer',
                  }
                : {};
        },
    },
};
</script>

<style lang="scss" scoped>
.pd-3 {
    margin-left: 2px;
}

.team-group {
    flex: 7 1 20%;
    display: flex;
    flex-flow: row nowrap;
}

.teams-list-move {
    transition: transform 1s;
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
    position: relative;
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

.edit {
    @extend .info;
}

.tt-edit {
    @extend .info;
    left: calc(100% - 2.5em - 0.5em - 3em);
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

.highlighted {
    transform: translateZ(0);
    animation: rotate 5s infinite linear;
    background: rgb(48, 255, 144); /* Old browsers */
    background: linear-gradient(
        to right,
        rgba(48, 255, 144, 1) 0%,
        rgba(237, 45, 237, 1) 25%,
        rgba(201, 152, 38, 1) 50%,
        rgba(48, 255, 230, 1) 75%,
        rgba(48, 255, 144, 1) 100%
    );
}

@keyframes rotate {
    from {
        background-position: -3000px;
    }
    to {
        background-position: 0px;
    }
}
</style>
