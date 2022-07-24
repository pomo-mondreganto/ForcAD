import { defineConfig } from 'vite';
import { createVuePlugin as vue } from 'vite-plugin-vue2';

const path = require('path');
export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
});
