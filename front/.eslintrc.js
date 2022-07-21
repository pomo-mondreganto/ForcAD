module.exports = {
    root: true,
    env: {
        node: true,
        es2021: true,
    },
    extends: ['eslint:recommended', 'plugin:vue/recommended', 'prettier'],
    rules: {
        'no-console': [
            process.env.NODE_ENV === 'production' ? 'error' : 'off',
            { allow: ['warn', 'error'] },
        ],
        'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
        'vue/multi-word-component-names': 'off',
    },
};
