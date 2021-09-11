module.exports = {
    root: true,
    env: {
        node: true,
    },
    extends: ['plugin:vue/essential', '@vue/prettier'],
    rules: {
        'no-console': [
            process.env.NODE_ENV === 'production' ? 'error' : 'off',
            { "allow": ["warn", "error"] },
        ],
        'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    },
    parserOptions: {
        parser: 'babel-eslint',
    },
};
