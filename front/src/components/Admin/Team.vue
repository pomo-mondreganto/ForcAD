<template>
    <form-wrapper
        v-if="team !== null"
        :title="message"
        :submit-callback="submitForm"
    >
        <p>
            Name:
            <input v-model="team.name" type="text" />
        </p>
        <p>
            IP:
            <input v-model="team.ip" type="text" />
        </p>
        <p>
            Token:
            <input v-model="team.token" type="text" />
        </p>
        <p>
            Highlighted:
            <input
                type="checkbox"
                :checked="team.highlighted"
                @input="team.highlighted = $event.target.checked"
            />
        </p>
        <p>
            Active:
            <input
                type="checkbox"
                :checked="team.active"
                @input="team.active = $event.target.checked"
            />
        </p>
    </form-wrapper>
</template>

<script>
import FormWrapper from '@/components/Lib/FormWrapper.vue';

export default {
    components: { FormWrapper },

    data: function () {
        return {
            error: null,
            team: null,
            teamId: null,
            message: null,
        };
    },

    watch: {
        $route: async function () {
            await this.updateData();
        },
    },

    created: async function () {
        await this.updateData();
    },

    methods: {
        updateData: async function () {
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
                const { data: team } = await this.$http.get(
                    `/admin/teams/${this.teamId}/`
                );
                this.team = team;
                this.message = `Editing team ${this.team.name} (${this.team.id})`;
            }
        },
        submitForm: async function () {
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
