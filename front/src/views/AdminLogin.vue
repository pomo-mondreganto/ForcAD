<template>
    <form-wrapper
        title="Log into the admin panel"
        :submit-callback="submitCallback"
    >
        <p>
            Username:
            <input v-model="username" type="text" placeholder="Username" />
        </p>
        <p>
            Password:
            <input v-model="password" type="password" placeholder="Password" />
        </p>
    </form-wrapper>
</template>

<script>
import FormWrapper from '@/components/Lib/FormWrapper.vue';

export default {
    components: {
        FormWrapper,
    },

    data: function () {
        return {
            username: null,
            password: null,
            error: null,
        };
    },

    methods: {
        submitCallback: async function () {
            await this.$http.post('/admin/login/', {
                username: this.username,
                password: this.password,
            });
            this.$router.push({ name: 'admin' }).catch(() => {});
        },
    },
};
</script>

<style lang="scss" scoped></style>
