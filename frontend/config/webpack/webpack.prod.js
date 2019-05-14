import CleanWebpackPlugin from 'clean-webpack-plugin';

import paths from './paths';

module.exports = {
    mode: 'production',
    output: {
        filename: `${paths.jsFolder}/[name].[hash].js`,
        path: paths.outputPath,
        chunkFilename: '[id].[chunkhash].js'
    },
    optimization: {
        splitChunks: {
            chunks: 'all'
        }
    },
    plugins: [new CleanWebpackPlugin()],
    devtool: 'source-map'
};
