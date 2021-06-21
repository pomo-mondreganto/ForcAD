import Vue from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';
import { apiUrl } from '@/config';

Vue.config.productionTip = false;

axios.defaults.baseURL = apiUrl;
axios.defaults.withCredentials = true;

Vue.prototype.$http = axios;
router.$http = axios;

new Vue({
    router,
    render: h => h(App),
}).$mount('#app');
