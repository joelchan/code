const path = require('path');
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');

module.exports = (baseConfig, env, defaultConfig) => {
  let loaders = [
    {
      test: /\.(ts|tsx)$/,
      exclude: ['.storybook'],
      use: [
        require.resolve("ts-loader"),
      ],
    },
    { test: /\.html$/, use: 'html-loader' },
      { test: /\.(png|svg)$/, use: 'url-loader?limit=10000' },
      { test: /\.(xml|txt)$/, use: 'raw-loader' },
      { test: /\.(jpg|gif)$/, use: 'file-loader' },
      { test: /\.(xml|txt)$/, use: 'raw-loader' }
  ]
  defaultConfig.resolve.alias = {
      ...defaultConfig.resolve.alias,
     "@assets": path.resolve(__dirname, '../src/assets/'),
     "@src": path.resolve(__dirname, '../src/')
}

  defaultConfig.module.rules.push(...loaders)
  defaultConfig.resolve.plugins = [new TsconfigPathsPlugin()]
      .concat(defaultConfig.resolve.plugins || []);

  defaultConfig.resolve.extensions.push('.ts', '.tsx');

  return defaultConfig;
};
