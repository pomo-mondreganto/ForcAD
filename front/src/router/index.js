import Vue from 'vue';
import VueRouter from 'vue-router';

import Scoreboard from '@/views/Scoreboard';
import LiveScoreboard from '@/views/LiveScoreboard';

Vue.use(VueRouter);

const routes = [
    {
        path: '/',
        name: 'index',
        component: Scoreboard,
    },
    {
        path: '/live/',
        name: 'live',
        component: LiveScoreboard,
    },
];

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes,
});

export default router;
