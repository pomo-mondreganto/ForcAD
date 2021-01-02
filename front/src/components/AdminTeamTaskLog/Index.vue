<template>
    <div v-if="error !== null">{{ error }}</div>
    <div v-else-if="teams !== null">
        <p>
            Team
            <b>{{ teamName }}</b>
            ({{ teamId }}) task
            <b>{{ taskName }}</b>
            ({{ taskId }}) history
        </p>
        <div class="table">
            <div class="row">
                <div class="round">round</div>
                <div class="status">status</div>
                <div class="score">score</div>
                <div class="flags">flags</div>
                <div class="checks">checks</div>
                <div class="public">public</div>
                <div class="private">private</div>
                <div class="command">command</div>
            </div>
            <div
                class="row"
                :class="`status-${status}`"
                v-for="{
                    id,
                    round,
                    status,
                    score,
                    stolen,
                    lost,
                    checks,
                    checks_passed,
                    public_message,
                    private_message,
                    command,
                } in teamtasks"
                :key="id"
            >
                <div class="round">{{ round }}</div>
                <div class="status">{{ status }}</div>
                <div class="score">{{ score }}</div>
                <div class="flags">+{{ stolen }}/-{{ lost }}</div>
                <div class="checks">{{ checks_passed }}/{{ checks }}</div>
                <div class="public">{{ public_message }}</div>
                <div class="private">{{ private_message }}</div>
                <div class="command">{{ command }}</div>
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
        timer: Number,
    },

    data: function() {
        return {
            error: null,
            taskId: null,
            teamId: null,
            teamtasks: null,
            teamName: null,
            taskName: null,
        };
    },

    methods: {
        openTeam: function(id) {
            clearInterval(this.timer);
            this.$router.push({ name: 'team', params: { id } }).catch(() => {});
        },
    },

    created: async function() {
        this.taskId = this.$route.params.taskId;
        this.teamId = this.$route.params.teamId;
        let r = await this.$http.get(
            `${serverUrl}/api/admin/teamtasks/?team_id=${this.teamId}&task_id=${this.taskId}`
        );
        this.teamtasks = r.data;

        r = await this.$http.get(`${serverUrl}/api/admin/teams/`);
        this.teamName = r.data.filter(({ id }) => id == this.teamId)[0].name;

        r = await this.$http.get(`${serverUrl}/api/admin/tasks/`);
        this.taskName = r.data.filter(({ id }) => id == this.taskId)[0].name;
    },
};
</script>

<style lang="scss" scoped>
.pd-3 {
    margin-left: 2px;
}

.default-team {
    background-color: white;
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
        min-height: 6em;
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
        word-wrap: break-word;
        border-left: 1px solid #c6cad1;
        min-width: 0;
    }

    border-top: 1px solid #c6cad1;
    border-left: 1px solid #c6cad1;
    border-right: 1px solid #c6cad1;

    &.highlighted > * {
        padding-top: 3px;
        padding-bottom: 3px;
    }

    &.highlighted > :first-child {
        padding-left: 3px;
    }

    &.highlighted > :last-child {
        padding-right: 3px;
    }
}

.round {
    flex: 1 1 0;
    display: flex;
    flex-flow: column nowrap;
    justify-content: center;
}

.status {
    @extend .round;
}

.score {
    @extend .round;
}

.flags {
    @extend .round;
}

.score {
    @extend .round;
}

.checks {
    @extend .round;
}

.public {
    @extend .round;
    flex: 1.5 2 15%;
    overflow: scroll;
}

.private {
    @extend .public;
}

.command {
    @extend .public;
}
</style>
