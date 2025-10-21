const path = require('path')
const HtmlPlugin = require('html-webpack-plugin')

module.exports = {
  entry: './index.js',
  output: {
    path: path.join(__dirname, 'dist'),
    filename: 'bundle.js',
  },
  plugins: [
    new HtmlPlugin({
      title: 'WASM Calculator',
      meta: {
        viewport: 'width=device-width, initial-scale=1.0'
      }
    }),
  ],
  mode: 'development',
  devtool: 'cheap-module-source-map',
  experiments: {
    asyncWebAssembly: true,
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'dist'),
    },
    compress: true,
    port: 8080,
  },
}
