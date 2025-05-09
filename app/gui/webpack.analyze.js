const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const webpackConfig = require('./webpack.config');

module.exports = (env, argv) => {
  const config = webpackConfig(env, argv);

  config.plugins.push(
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      reportFilename: 'bundle-report.html',
      openAnalyzer: true
    })
  );

  return config;
};
