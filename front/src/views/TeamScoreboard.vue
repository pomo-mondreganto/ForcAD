<template>
    <div>
        <statuses />
        <team-scoreboard />
    </div>
</template>

<script>
import Statuses from '@/components/General/Statuses.vue';
import TeamScoreboard from '@/components/Scores/TeamScoreboard.vue';

export default {
    components: {
        TeamScoreboard,
        Statuses,
    },
};
</script>

<style lang="scss" scoped></style>
