<template>
    <div id="app">
        <header>
            <topbar :round="round" />
        </header>
        <container>
            <form-wrapper
                title="Log into the admin panel"
                :submitCallback="submitCallback"
            >
                <p>
                    Username:
                    <input
                        type="text"
                        v-model="username"
                        placeholder="Username"
                    />
                </p>
                <p>
                    Password:
                    <input
                        type="password"
                        v-model="password"
                        placeholder="Password"
                    />
                </p>
            </form-wrapper>
        </container>
        <footer class="footer">
            Powered by
            <span class="team">C4T BuT S4D</span> CTF team
        </footer>
    </div>
</template>

<script>
import Container from '@/components/Lib/Container';
import Topbar from '@/components/General/Topbar';
import FormWrapper from '@/components/Lib/FormWrapper';

export default {
    components: {
        Container,
        Topbar,
        FormWrapper,
    },

    data: function() {
        return {
            username: null,
            password: null,
            error: null,
            round: 0,
        };
    },

    methods: {
        updateRound: function(round) {
            this.round = round;
        },
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

<style lang="scss" scoped>
#app {
    height: 100%;
    display: flex;

    flex-flow: column nowrap;

    & > :nth-child(2) {
        flex-grow: 1;
    }
}

.footer {
    text-align: center;
    margin-top: 3em;
}
</style>
