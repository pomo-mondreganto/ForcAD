<template>
    <div>
        <statuses />
        <scoreboard />
    </div>
</template>

<script>
import Scoreboard from '@/components/Scores/Scoreboard';
import Statuses from '@/components/General/Statuses';

export default {
    components: {
        Scoreboard,
        Statuses,
    },
};
</script>

<style lang="scss" scoped></style>
