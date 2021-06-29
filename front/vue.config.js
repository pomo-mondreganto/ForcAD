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
                minSize: 200000,
                maxSize: 500000,
            },
        },
    },
};
