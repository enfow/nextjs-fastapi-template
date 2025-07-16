// prettier.config.js
module.exports = {
  // Your other Prettier rules...
  semi: true,
  singleQuote: true,
  trailingComma: 'es5',

  // Plugin configuration
  plugins: ['@trivago/prettier-plugin-sort-imports'],
  
  // Rule configuration for the plugin
  importOrder: [
    '^react(.*)$', // React and react-related imports
    '<THIRD_PARTY_MODULES>', // All other 3rd party modules
    '^@/components/(.*)$', // Absolute imports for components
    '^@/lib/(.*)$', // Absolute imports for lib
    '^[./]', // Relative imports
  ],
  importOrderSeparation: true, // Adds newlines between groups
  importOrderSortSpecifiers: true, // Sorts specifiers within an import (e.g., {b, a} -> {a, b})
};