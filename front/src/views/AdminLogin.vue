<template>
    <form-wrapper
        title="Log into the admin panel"
        :submitCallback="submitCallback"
    >
        <p>
            Username:
            <input type="text" v-model="username" placeholder="Username" />
        </p>
        <p>
            Password:
            <input type="password" v-model="password" placeholder="Password" />
        </p>
    </form-wrapper>
</template>

<script>
import FormWrapper from '@/components/Lib/FormWrapper';

export default {
    components: {
        FormWrapper,
    },

    data: function() {
        return {
            username: null,
            password: null,
            error: null,
        };
    },

    methods: {
        submitCallback: async function() {
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
