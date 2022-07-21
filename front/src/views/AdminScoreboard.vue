<template>
    <div>
        <div class="create-group">
            <button class="create-btn" @click="createTask">Create task</button>
            <button class="create-btn" @click="createTeam">Create team</button>
        </div>
        <admin-scoreboard />
    </div>
</template>

<script>
import AdminScoreboard from '@/components/Admin/Scoreboard.vue';

export default {
    components: {
        AdminScoreboard,
    },

    methods: {
        createTask: async function() {
            this.$router.push({ name: 'createTask' }).catch(() => {});
        },

        createTeam: async function() {
            this.$router.push({ name: 'createTeam' }).catch(() => {});
        },
    },
};
</script>

<style lang="scss" scoped>
.create-group {
    display: flex;
    flex-flow: row-reverse;
}

.create-btn {
    font-size: 1em;
    margin: 1em;
}
</style>
