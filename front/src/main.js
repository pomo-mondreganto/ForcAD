import Vue from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';
import store from '@/store';
import { apiUrl } from '@/config';
import DefaultLayout from '@/layouts/DefaultLayout';
import EmptyLayout from '@/layouts/EmptyLayout';

Vue.config.productionTip = false;

axios.defaults.baseURL = apiUrl;
axios.defaults.withCredentials = true;

Vue.prototype.$http = axios;
router.$http = axios;
store.$http = axios;

Vue.component('default-layout', DefaultLayout);
Vue.component('empty-layout', EmptyLayout);

new Vue({
    router,
    store,
    render: h => h(App),
}).$mount('#app');
