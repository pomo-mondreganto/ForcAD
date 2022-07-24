<template>
    <score-table
        v-if="teams !== null"
        head-row-title="#"
        :team-clickable="true"
        :tasks="tasks"
        :teams="teams"
        @openTeam="openTeam"
    />
</template>

<script>
import ScoreTable from '@/components/Lib/ScoreTable.vue';
import { mapState } from 'vuex';

export default {
    components: {
        ScoreTable,
    },

    computed: mapState(['teams', 'tasks']),

    methods: {
        openTeam: function (id) {
            this.$router.push({ name: 'team', params: { id } }).catch(() => {});
        },
    },
};
</script>

<style lang="scss" scoped></style>
