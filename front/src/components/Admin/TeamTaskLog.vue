<template>
    <error-box :error="error">
        <div>
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
                    v-for="tt in teamtasks"
                    :key="tt.id"
                    class="row content-row"
                    :style="{
                        backgroundColor: getTeamTaskBackground(tt.status),
                    }"
                >
                    <div class="round">
                        {{ tt.round }}
                    </div>
                    <div class="status">
                        {{ tt.status }}
                    </div>
                    <div class="score">
                        {{ tt.score }}
                    </div>
                    <div class="flags">+{{ tt.stolen }}/-{{ tt.lost }}</div>
                    <div class="checks">
                        {{ tt.checks_passed }}/{{ tt.checks }}
                    </div>
                    <div class="public">
                        {{ tt.public_message }}
                    </div>
                    <div class="private">
                        {{ tt.private_message }}
                    </div>
                    <div class="command">
                        {{ tt.command }}
                    </div>
                </div>
            </div>
        </div>
    </error-box>
</template>

<script>
import { getTeamTaskBackground } from '@/utils/colors';
import ErrorBox from '@/components/Lib/ErrorBox.vue';
import '@/assets/table.scss';

export default {
    components: {
        ErrorBox,
    },

    data: function () {
        return {
            error: null,
            taskId: null,
            teamId: null,
            teamtasks: null,
            teamName: null,
            taskName: null,

            getTeamTaskBackground,
        };
    },

    created: async function () {
        try {
            this.taskId = this.$route.params.taskId;
            this.teamId = this.$route.params.teamId;
            let r = await this.$http.get('/admin/teamtasks/', {
                params: { team_id: this.teamId, task_id: this.taskId },
            });
            this.teamtasks = r.data;

            const {
                data: { name: teamName },
            } = await this.$http.get(`/admin/teams/${this.teamId}/`);
            this.teamName = teamName;

            const {
                data: { name: taskName },
            } = await this.$http.get(`/admin/tasks/${this.taskId}/`);
            this.taskName = taskName;
        } catch (e) {
            console.error(e);
            this.error = 'Error occured while fetching data.';
        }
    },

    methods: {
        openTeam: function (id) {
            this.$router.push({ name: 'team', params: { id } }).catch(() => {});
        },
    },
};
</script>

<style lang="scss" scoped>
.content-row {
    & > :not(:first-child) {
        border-left: 1px solid #c6cad1;
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
    overflow-x: auto;
}

.private {
    @extend .public;
}

.command {
    @extend .public;
}
</style>
