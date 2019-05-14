import webpack from 'webpack';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import MiniCssExtractPlugin from 'mini-css-extract-plugin';

import paths from './paths';

const rules = [
    {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
            loader: 'babel-loader'
        }
    },
    {
        test: /\.s?css$/,
        use: [
            {
                loader: MiniCssExtractPlugin.loader,
                options: {
                    hmr: process.env.NODE_ENV === 'development',
                    reloadAll: true
                }
            },
            'css-loader',
            {
                loader: 'sass-loader',
                options: {
                    // eslint-disable-next-line global-require
                    implementation: require('sass')
                }
            }
        ]
    },
    {
        test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'file-loader'
    },
    {
        test: /\.(woff|woff2)$/,
        loader: 'url-loader?prefix=font/&limit=5000'
    },
    {
        test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
        loader: 'url-loader?limit=10000&mimetype=application/octet-stream'
    },
    {
        test: /\.(jpe?g|png|gif|svg)$/i,
        use: ['url-loader?limit=10000', 'img-loader']
    }
];

module.exports = {
    entry: paths.entryPath,
    module: {
        rules
    },
    resolve: {
        modules: ['src', '.', 'node_modules'],
        extensions: ['*', '.js', '.scss', '.css']
    },
    plugins: [
        new webpack.ProgressPlugin(),
        new HtmlWebpackPlugin({
            template: paths.templatePath,
            minify: {
                collapseInlineTagWhitespace: true,
                collapseWhitespace: true,
                preserveLineBreaks: true,
                minifyURLs: true,
                removeComments: true,
                removeAttributeQuotes: true
            }
        }),
        new MiniCssExtractPlugin({
            filename:
                process.env.NODE_ENV === 'development'
                    ? '[name].css'
                    : `${paths.cssFolder}/[name].[hash].css`,
            chunkFilename:
                process.env.NODE_ENV === 'development'
                    ? '[id].css'
                    : '[id].[chunkhash].css'
        })
    ]
};
