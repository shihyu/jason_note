const path = require('path');

const GlobEntries = require('webpack-glob-entries');

module.exports = {
  // 1. 設置模式
  mode: 'production', // 或 'development'，production 會有優化和壓縮

  // 2. 設置入口檔案
  entry: GlobEntries('./src/scenarios/*.ts'),

  // 3. 設置輸出檔案
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].bundle.js', // 最終打包後 k6 要執行的 JS 檔案
    libraryTarget: 'commonjs', // 確保輸出格式兼容 k6
  },

  // 4. 解析規則：如何處理不同類型的檔案
  resolve: {
    extensions: ['.ts', '.js'], // 讓 Webpack 識別 .ts 和 .js 檔案
  },

  // 5. 模組規則：使用 ts-loader 處理 .ts 檔案
  module: {
    rules: [
      {
        test: /\.ts$/, // 匹配所有 .ts 檔案
        use: 'ts-loader', // 使用 ts-loader 進行轉譯
        exclude: /node_modules/,
      },
    ],
  },

  // 6. 關鍵：排除 k6 內建模組 (Externalization)
  // 告訴 Webpack 不要將這些模組打包進去，讓 k6 執行時自行提供。
  externals: {
    'k6': 'k6',
    'k6/data': 'k6/data',
    'k6/http': 'k6/http',
    'k6/options': 'k6/options',
    'k6/metrics': 'k6/metrics',
    'k6/ws': 'k6/ws',
    'k6/x/kafka': 'k6/x/kafka',
    'k6/net/grpc': 'k6/net/grpc',
  },

  // 7. 將 devtool 設為 false，避免 k6 執行時出現問題
  devtool: false,
};