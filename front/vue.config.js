module.exports = {
    pluginOptions: {
        webpackBundleAnalyzer: {
            openAnalyzer: false,
            analyzerMode: 'disabled',
        },
    },
    configureWebpack: {
        optimization: {
            splitChunks: {
                chunks: 'all',
            },
        },
    },
};
