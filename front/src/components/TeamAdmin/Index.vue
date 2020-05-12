<template>
    <div v-if="error !== null">
        {{ error }}
    </div>
    <form @submit.prevent="submitForm" v-else-if="team !== null">
        <p>{{ message }}</p>
        <p>
            Name:
            <input type="text" v-model="team.name" />
        </p>
        <p>
            IP:
            <input type="text" v-model="team.ip" />
        </p>
        <p>
            Token:
            <input type="text" v-model="team.token" />
        </p>
        <p>
            Highlighted:
            <input
                type="checkbox"
                @input="team.highlighted = $event.target.checked"
                :checked="team.highlighted"
            />
        </p>
        <p>
            Active:
            <input
                type="checkbox"
                @input="team.active = $event.target.checked"
                :checked="team.active"
            />
        </p>
        <input type="submit" value="Submit" />
    </form>
</template>

<script>
import { serverUrl } from '@/config';

export default {
    props: {
        updateRound: Function,
        updateRoundStart: Function,
    },

    data: function() {
        return {
            error: null,
            team: null,
            teamId: null,
            message: null,
        };
    },

    created: async function() {
        await this.updateData();
    },

    watch: {
        $route: async function() {
            await this.updateData();
        },
    },

    methods: {
        updateData: async function() {
            this.teamId = this.$route.params.id;
            if (!this.teamId) {
                this.team = {
                    name: '',
                    ip: '',
                    token: '',
                    highlighted: false,
                    active: true,
                };
                this.message = 'Creating team';
            } else {
                const { data: teams } = await this.$http.get(
                    `${serverUrl}/api/admin/teams/`
                );
                this.team = teams.filter(({ id }) => id == this.teamId)[0];
                this.message = `Editing team ${this.team.id} ${this.team.name}`;
            }
        },
        submitForm: async function() {
            if (!this.teamId) {
                const { data: team } = await this.$http.post(
                    `${serverUrl}/api/admin/teams/`,
                    this.team
                );
                this.$router
                    .push({ name: 'teamAdmin', params: { id: team.id } })
                    .catch(() => {});
            } else {
                const { data: team } = await this.$http.put(
                    `${serverUrl}/api/admin/teams/${this.teamId}/`,
                    this.team
                );
                this.team = team;
            }
        },
    },
};
</script>

<style lang="scss" scoped></style>
