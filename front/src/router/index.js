import Vue from 'vue';
import VueRouter from 'vue-router';

import Scoreboard from '@/views/Scoreboard';
import LiveScoreboard from '@/views/LiveScoreboard';
import TeamScoreboard from '@/views/TeamScoreboard';

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
    {
        path: '/team/:id/',
        name: 'team',
        component: TeamScoreboard,
    },
];

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes,
});

export default router;
