import webpack from 'webpack';

import paths from './paths';

module.exports = {
    mode: 'development',
    output: {
        filename: '[name].js',
        path: paths.outputPath,
        chunkFilename: '[id].js'
    },
    optimization: {
        splitChunks: {
            chunks: 'all'
        }
    },
    devServer: {
        contentBase: paths.outputPath,
        compress: true,
        hot: true,
        historyApiFallback: true,
        host: '127.0.0.1',
        port: 3000
    },
    plugins: [new webpack.HotModuleReplacementPlugin()]
};
