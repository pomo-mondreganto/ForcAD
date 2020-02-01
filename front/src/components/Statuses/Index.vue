<template>
    <div class="statuses">
        <div
            v-for="status in statuses"
            :key="status"
            :class="`status-${status}`"
            class="status-cell"
        >
            {{ statusesNames[status] }}
        </div>
    </div>
</template>

<script>
import { statuses, statusesNames } from '@/config';

export default {
    data: function() {
        return {
            statuses,
            statusesNames,
        };
    },
};
</script>

<style lang="scss" scoped>
.statuses {
    margin-top: 2em;
    margin-bottom: 2em;

    display: flex;
    flex-flow: row nowrap;

    & > * {
        flex: 1 1 auto;
        text-align: center;
        padding: 0.5em;
    }

    .status-cell {
        display: flex;
        flex-flow: column nowrap;
        justify-content: center;
    }
}
</style>
