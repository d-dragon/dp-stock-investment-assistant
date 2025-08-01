// webpack.config.js - Performance optimizations for development
const path = require('path');

module.exports = {
  mode: 'development',
  
  // Optimize resolve
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      'components': path.resolve(__dirname, 'src/components'),
      'utils': path.resolve(__dirname, 'src/utils'),
    },
    modules: ['node_modules', path.resolve(__dirname, 'src')],
  },

  // Development optimizations
  optimization: {
    removeAvailableModules: false,
    removeEmptyChunks: false,
    splitChunks: false,
  },

  // Cache configuration
  cache: {
    type: 'filesystem',
    cacheDirectory: path.resolve(__dirname, 'node_modules/.cache/webpack'),
    buildDependencies: {
      config: [__filename],
    },
  },

  // Performance hints
  performance: {
    hints: 'warning',
    maxEntrypointSize: 250000,
    maxAssetSize: 250000,
  },

  // Dev server optimizations
  devServer: {
    hot: true,
    liveReload: false, // Use hot reload instead
    compress: true,
    historyApiFallback: true,
  },

  // Module rules
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            cacheDirectory: true,
            cacheCompression: false,
          },
        },
      },
    ],
  },
};
