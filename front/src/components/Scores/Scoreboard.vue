<template>
    <score-table
        v-if="teams !== null"
        headRowTitle="#"
        @openTeam="openTeam"
        :teamClickable="true"
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
    },

    computed: mapState(['teams', 'tasks']),
};
</script>

<style lang="scss" scoped></style>
