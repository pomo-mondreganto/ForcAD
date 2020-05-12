<template>
    <div id="app">
        <header>
            <topbar :round="round" />
        </header>
        <container>
            <form @submit.prevent="submitForm">
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
                <p v-if="error !== null" class="error-message">{{ error }}</p>
                <input type="submit" value="Submit" />
            </form>
        </container>
        <footer class="footer">
            Powered by
            <span class="team">C4T BuT S4D</span> CTF team
        </footer>
    </div>
</template>

<script>
import Container from '@/components/Container/Index';
import Topbar from '@/components/Topbar/Index';
import { serverUrl } from '@/config';

export default {
    components: {
        Container,
        Topbar,
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
        submitForm: async function() {
            try {
                await this.$http.post(`${serverUrl}/api/admin/login/`, {
                    username: this.username,
                    password: this.password,
                });
                this.$router.push({ name: 'admin' }).catch(() => {});
            } catch (e) {
                this.error = e.response.data;
            }
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

.error-message {
    color: red;
}
</style>
