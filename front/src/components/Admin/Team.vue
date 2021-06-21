<template>
    <form-wrapper
        v-if="task !== null"
        :title="message"
        :submitCallback="submitForm"
    >
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
    </form-wrapper>
</template>

<script>
import FormWrapper from '@/components/Lib/FormWrapper';

export default {
    components: { FormWrapper },

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
                const { data: teams } = await this.$http.get('/admin/teams/');
                this.team = teams.filter(({ id }) => id == this.teamId)[0];
                this.message = `Editing team ${this.team.id} ${this.team.name}`;
            }
        },
        submitForm: async function() {
            if (!this.teamId) {
                const { data: team } = await this.$http.post(
                    '/admin/teams/',
                    this.team
                );
                this.$router
                    .push({ name: 'teamAdmin', params: { id: team.id } })
                    .catch(() => {});
            } else {
                const { data: team } = await this.$http.put(
                    `/admin/teams/${this.teamId}/`,
                    this.team
                );
                this.team = team;
                await this.updateData();
            }
        },
    },
};
</script>

<style lang="scss" scoped></style>
