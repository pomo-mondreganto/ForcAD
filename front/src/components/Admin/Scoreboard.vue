<template>
    <score-table
        v-if="teams !== null"
        headRowTitle="#"
        @openTeam="openTeam"
        @openTeamAdmin="openTeamAdmin"
        @openTaskAdmin="openTaskAdmin"
        @openTeamTaskHistory="openTeamTaskHistory"
        :teamClickable="true"
        :admin="true"
        :tasks="tasks"
        :teams="teams"
    />
</template>

<script>
import ScoreTable from '@/components/Lib/ScoreTable';
import { mapState } from 'vuex';

export default {
    components: {
        ScoreTable,
    },

    methods: {
        openTeam: function(id) {
            this.$router.push({ name: 'team', params: { id } }).catch(() => {});
        },
        openTaskAdmin: function(id) {
            this.$router
                .push({ name: 'taskAdmin', params: { id } })
                .catch(() => {});
        },
        openTeamAdmin: function(id) {
            this.$router
                .push({ name: 'teamAdmin', params: { id } })
                .catch(() => {});
        },
        openTeamTaskHistory: function(teamId, taskId) {
            this.$router
                .push({
                    name: 'adminTeamTaskLog',
                    params: { teamId: teamId, taskId: taskId },
                })
                .catch(() => {});
        },
    },

    computed: mapState(['tasks', 'teams']),
};
</script>

<style lang="scss" scoped></style>
