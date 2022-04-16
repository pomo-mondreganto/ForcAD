<template>
    <div>
        <statuses />
        <team-scoreboard />
    </div>
</template>

<script>
import Statuses from '@/components/General/Statuses';
import TeamScoreboard from '@/components/Scores/TeamScoreboard';

export default {
    components: {
        TeamScoreboard,
        Statuses,
    },
};
</script>

<style lang="scss" scoped></style>
