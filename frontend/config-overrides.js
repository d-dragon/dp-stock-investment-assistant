const { override, addWebpackPlugin, addWebpackResolve } = require('customize-cra');
const webpack = require('webpack');

module.exports = override(
  // Add webpack optimizations
  addWebpackPlugin(
    new webpack.optimize.AggressiveSplittingPlugin({
      minSize: 30000,
      maxSize: 50000,
    })
  ),
  
  // Resolve optimizations
  addWebpackResolve({
    fallback: {
      "crypto": false,
      "stream": false,
      "buffer": false
    }
  }),
  
  // Custom webpack config
  (config, env) => {
    // Optimize for development
    if (env === 'development') {
      config.optimization = {
        ...config.optimization,
        removeAvailableModules: false,
        removeEmptyChunks: false,
        splitChunks: false,
      };
    }
    
    return config;
  }
);
