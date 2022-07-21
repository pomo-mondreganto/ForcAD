<template>
    <score-table
        v-if="teams !== null"
        head-row-title="#"
        :team-clickable="true"
        :admin="true"
        :tasks="tasks"
        :teams="teams"
        @openTeam="openTeam"
        @openTeamAdmin="openTeamAdmin"
        @openTaskAdmin="openTaskAdmin"
        @openTeamTaskHistory="openTeamTaskHistory"
    />
</template>

<script>
import ScoreTable from '@/components/Lib/ScoreTable.vue';
import { mapState } from 'vuex';

export default {
    components: {
        ScoreTable,
    },

    computed: mapState(['tasks', 'teams']),

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
};
</script>

<style lang="scss" scoped></style>
