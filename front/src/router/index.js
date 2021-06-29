import Vue from 'vue';
import VueRouter from 'vue-router';

import { serverUrl } from '@/config';

Vue.use(VueRouter);

const routes = [
    {
        path: '/',
        name: 'index',
        component: () => import('@/views/Scoreboard'),
    },
    {
        path: '/live/',
        name: 'live',
        component: () => import('@/views/LiveScoreboard'),
        meta: {
            layout: 'empty-layout',
        },
    },
    {
        path: '/team/:id/',
        name: 'team',
        component: () => import('@/views/TeamScoreboard'),
    },
    {
        path: '/admin/login/',
        name: 'adminLogin',
        component: () => import('@/views/AdminLogin'),
    },
    {
        path: '/admin/',
        name: 'admin',
        component: () => import('@/views/AdminScoreboard'),
        meta: {
            auth: true,
        },
    },
    {
        path: '/admin/task/:id/',
        name: 'taskAdmin',
        component: () => import('@/views/TaskAdmin'),
        meta: {
            auth: true,
        },
    },
    {
        path: '/admin/team/:id/',
        name: 'teamAdmin',
        component: () => import('@/views/TeamAdmin'),
        meta: {
            auth: true,
        },
    },
    {
        path: '/admin/create_task/',
        name: 'createTask',
        component: () => import('@/views/TaskAdmin'),
        meta: {
            auth: true,
        },
    },
    {
        path: '/admin/create_team/',
        name: 'createTeam',
        component: () => import('@/views/TeamAdmin'),
        meta: {
            auth: true,
        },
    },
    {
        path: '/admin/teamtask_log/team/:teamId/task/:taskId/',
        name: 'adminTeamTaskLog',
        component: () => import('@/views/AdminTeamTaskLog'),
        meta: {
            auth: true,
        },
    },
];

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes,
});

router.beforeEach(async function(to, from, next) {
    if (to.meta.auth) {
        let ok = false;
        try {
            await router.$http.get(`${serverUrl}/api/admin/status/`);
            ok = true;
        } catch (e) {
            next({
                name: 'adminLogin',
            });
        }
        if (ok) {
            next();
        }
    } else {
        next();
    }
});

export default router;
