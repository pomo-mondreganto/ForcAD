import Vue from 'vue';
import VueRouter from 'vue-router';

import { serverUrl } from '@/config';

const Scoreboard = () => import('@/views/Scoreboard.vue');
const LiveScoreboard = () => import('@/views/LiveScoreboard.vue');
const TeamScoreboard = () => import('@/views/TeamScoreboard.vue');

const AdminLogin = () => import('@/views/AdminLogin.vue');
const AdminScoreboard = () => import('@/views/AdminScoreboard.vue');
const TaskAdmin = () => import('@/views/TaskAdmin.vue');
const TeamAdmin = () => import('@/views/TeamAdmin.vue');
const AdminTeamTaskLog = () => import('@/views/AdminTeamTaskLog.vue');

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
        meta: {
            layout: 'empty-layout',
        },
    },
    {
        path: '/team/:id/',
        name: 'team',
        component: TeamScoreboard,
    },
    {
        path: '/admin/login/',
        name: 'adminLogin',
        component: AdminLogin,
    },
    {
        path: '/admin/',
        name: 'admin',
        component: AdminScoreboard,
        meta: {
            auth: true,
        },
    },
    {
        path: '/admin/task/:id/',
        name: 'taskAdmin',
        component: TaskAdmin,
        meta: {
            auth: true,
        },
    },
    {
        path: '/admin/team/:id/',
        name: 'teamAdmin',
        component: TeamAdmin,
        meta: {
            auth: true,
        },
    },
    {
        path: '/admin/create_task/',
        name: 'createTask',
        component: TaskAdmin,
        meta: {
            auth: true,
        },
    },
    {
        path: '/admin/create_team/',
        name: 'createTeam',
        component: TeamAdmin,
        meta: {
            auth: true,
        },
    },
    {
        path: '/admin/teamtask_log/team/:teamId/task/:taskId/',
        name: 'adminTeamTaskLog',
        component: AdminTeamTaskLog,
        meta: {
            auth: true,
        },
    },
];

const router = new VueRouter({
    mode: 'history',
    base: '/',
    routes,
});

router.beforeEach(async function (to, from, next) {
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
