<template>
    <div>
        <statuses />
        <scoreboard />
    </div>
</template>

<script>
import Scoreboard from '@/components/Scores/Scoreboard.vue';
import Statuses from '@/components/General/Statuses.vue';

export default {
    components: {
        Scoreboard,
        Statuses,
    },
};
</script>

<style lang="scss" scoped></style>
