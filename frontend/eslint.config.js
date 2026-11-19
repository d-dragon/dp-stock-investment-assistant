const react = require('eslint-plugin-react')
const tseslint = require('typescript-eslint')

const directionMessage =
  'Dependency direction is app → features → platform / design-system.'

const parserBlock = {
  languageOptions: {
    parser: tseslint.parser,
    parserOptions: {
      ecmaFeatures: { jsx: true },
      sourceType: 'module',
    },
  },
}

module.exports = [
  {
    ignores: ['node_modules/**', 'dist/**', 'build/**', 'coverage/**'],
  },
  {
    files: ['src/**/*.{js,jsx,ts,tsx}'],
    ...parserBlock,
    plugins: { react },
    settings: { react: { version: '18.3' } },
    rules: {
      'react/no-danger': 'error',
    },
  },
  {
    files: ['eslint-fixtures/**/*.{ts,tsx}'],
    ...parserBlock,
    plugins: { react },
    settings: { react: { version: '18.3' } },
    rules: {
      'react/no-danger': 'error',
    },
  },
  {
    files: ['eslint-fixtures/b1-rule1-reverse-import.ts'],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['**/features/**'],
              message: `${directionMessage} Do not import a feature from platform or design-system.`,
            },
          ],
        },
      ],
    },
  },
  {
    files: ['eslint-fixtures/b1-rule2-deep-import.ts'],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['**/features/*/**'],
              message: 'Import a feature only through its index. No sibling-feature or deep imports.',
            },
          ],
        },
      ],
    },
  },
  {
    files: [
      'eslint-fixtures/b1-rule3-fetch.ts',
      'src/app/**/*.{js,jsx,ts,tsx}',
      'src/features/**/*.{js,jsx,ts,tsx}',
      'src/design-system/**/*.{js,jsx,ts,tsx}',
      'src/platform/**/*.{js,jsx,ts,tsx}',
    ],
    ignores: ['src/platform/api/**', 'src/platform/stream/**', '**/*.test.ts', '**/*.test.tsx'],
    ...parserBlock,
    rules: {
      'no-restricted-globals': ['error', 'fetch', 'XMLHttpRequest', 'EventSource', 'WebSocket'],
      'no-restricted-imports': [
        'error',
        {
          paths: [
            {
              name: 'socket.io-client',
              message: 'Do not use socket.io-client. Chat transport is fetch-based SSE.',
            },
            {
              name: 'axios',
              message: 'Do not use axios. Call fetch only inside platform/api and platform/stream.',
            },
            {
              name: 'lightweight-charts',
              message: 'Import lightweight-charts only from platform/chart.',
            },
            {
              name: 'chart.js',
              message: 'Import chart.js only from platform/stat-chart.',
            },
          ],
        },
      ],
      'no-restricted-syntax': [
        'error',
        {
          selector: "CallExpression[callee.name='fetch']",
          message: 'fetch is allowed only inside platform/api and platform/stream.',
        },
        {
          selector: "NewExpression[callee.name='XMLHttpRequest']",
          message: 'XMLHttpRequest is allowed only inside platform/api and platform/stream.',
        },
        {
          selector: "NewExpression[callee.name='WebSocket']",
          message: 'WebSocket is not allowed.',
        },
        {
          selector: "NewExpression[callee.name='EventSource']",
          message: 'EventSource is not allowed.',
        },
        {
          selector: "Literal[value='meta'], Literal[value='token'], Literal[value='final']",
          message: 'Stream event names stay in the StreamEvent union and legacyChatAdapter.',
        },
      ],
    },
  },
  {
    files: ['src/platform/**/*.{js,jsx,ts,tsx}', 'src/design-system/**/*.{js,jsx,ts,tsx}'],
    ignores: [
      'src/platform/api/**',
      'src/platform/stream/**',
      'src/platform/chart/**',
      'src/platform/stat-chart/**',
    ],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          paths: [
            {
              name: 'socket.io-client',
              message: 'Do not use socket.io-client. Chat transport is fetch-based SSE.',
            },
            {
              name: 'axios',
              message: 'Do not use axios. Call fetch only inside platform/api and platform/stream.',
            },
            {
              name: 'lightweight-charts',
              message: 'Import lightweight-charts only from platform/chart.',
            },
            {
              name: 'chart.js',
              message: 'Import chart.js only from platform/stat-chart.',
            },
          ],
          patterns: [
            {
              group: ['**/features/**', '**/app/**'],
              message: directionMessage,
            },
          ],
        },
      ],
    },
  },
  {
    files: ['src/features/**/*.{js,jsx,ts,tsx}'],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          paths: [
            {
              name: 'socket.io-client',
              message: 'Do not use socket.io-client. Chat transport is fetch-based SSE.',
            },
            {
              name: 'axios',
              message: 'Do not use axios. Call fetch only inside platform/api and platform/stream.',
            },
            {
              name: 'lightweight-charts',
              message: 'Import lightweight-charts only from platform/chart.',
            },
            {
              name: 'chart.js',
              message: 'Import chart.js only from platform/stat-chart.',
            },
          ],
          patterns: [
            {
              group: ['**/app/**', '**/features/*/components/**', '**/features/*/hooks/**', '**/features/*/model/**'],
              message: 'No sibling-feature or deep imports. Import a feature only through its index.',
            },
          ],
        },
      ],
    },
  },
  {
    files: [
      'src/platform/api/**/*.{js,jsx,ts,tsx}',
      'src/platform/stream/**/*.{js,jsx,ts,tsx}',
      'src/components/**/*.{js,jsx,ts,tsx}',
      'src/services/**/*.{js,jsx,ts,tsx}',
      'src/utils/**/*.{js,jsx,ts,tsx}',
      'src/types/**/*.{js,jsx,ts,tsx}',
      'src/test/**/*.{js,jsx,ts,tsx}',
      'src/*.{js,jsx,ts,tsx}',
      'eslint-fixtures/b2-socket-io-import.ts',
    ],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          paths: [
            {
              name: 'socket.io-client',
              message: 'Do not use socket.io-client. Chat transport is fetch-based SSE.',
            },
            {
              name: 'axios',
              message: 'Do not use axios. Call fetch only inside platform/api and platform/stream.',
            },
            {
              name: 'lightweight-charts',
              message: 'Import lightweight-charts only from platform/chart.',
            },
            {
              name: 'chart.js',
              message: 'Import chart.js only from platform/stat-chart.',
            },
          ],
        },
      ],
    },
  },
  {
    files: [
      'eslint-fixtures/b2-stream-event-outside-union.ts',
      'src/components/**/*.{js,jsx,ts,tsx}',
      'src/services/**/*.{js,jsx,ts,tsx}',
      'src/utils/**/*.{js,jsx,ts,tsx}',
      'src/types/**/*.{js,jsx,ts,tsx}',
      'src/platform/api/**/*.{js,jsx,ts,tsx}',
      'src/platform/stream/**/*.{js,jsx,ts,tsx}',
      'src/*.{js,jsx,ts,tsx}',
    ],
    ignores: [
      'src/platform/stream/types.ts',
      'src/platform/stream/legacyChatAdapter.ts',
      '**/*.test.ts',
      '**/*.test.tsx',
    ],
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector: "Literal[value='meta'], Literal[value='token'], Literal[value='final']",
          message: 'Stream event names stay in the StreamEvent union and legacyChatAdapter.',
        },
      ],
    },
  },
  {
    files: ['src/platform/chart/**/*.{js,jsx,ts,tsx}', 'src/platform/stat-chart/**/*.{js,jsx,ts,tsx}'],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          paths: [
            {
              name: 'socket.io-client',
              message: 'Do not use socket.io-client. Chat transport is fetch-based SSE.',
            },
            {
              name: 'axios',
              message: 'Do not use axios. Call fetch only inside platform/api and platform/stream.',
            },
          ],
          patterns: [
            {
              group: ['**/features/**', '**/app/**'],
              message: directionMessage,
            },
          ],
        },
      ],
    },
  },
  {
    files: [
      'eslint-fixtures/b4-lightweight-charts-outside.ts',
      'eslint-fixtures/b4-chartjs-outside.ts',
    ],
    rules: {
      'no-restricted-imports': [
        'error',
        {
          paths: [
            {
              name: 'lightweight-charts',
              message: 'Import lightweight-charts only from platform/chart.',
            },
            {
              name: 'chart.js',
              message: 'Import chart.js only from platform/stat-chart.',
            },
          ],
        },
      ],
    },
  },
  {
    files: [
      'src/**/*.{js,jsx,ts,tsx}',
      'eslint-fixtures/b4-market-var-outside.tsx',
      'eslint-fixtures/b4-state-var-outside.tsx',
      'eslint-fixtures/b4-arbitrary-color.tsx',
    ],
    ignores: [
      'src/platform/api/**',
      'src/platform/stream/**',
      '**/*.test.ts',
      '**/*.test.tsx',
    ],
    ...parserBlock,
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector: "CallExpression[callee.name='fetch']",
          message: 'fetch is allowed only inside platform/api and platform/stream.',
        },
        {
          selector: "NewExpression[callee.name='XMLHttpRequest']",
          message: 'XMLHttpRequest is allowed only inside platform/api and platform/stream.',
        },
        {
          selector: "NewExpression[callee.name='WebSocket']",
          message: 'WebSocket is not allowed.',
        },
        {
          selector: "NewExpression[callee.name='EventSource']",
          message: 'EventSource is not allowed.',
        },
        {
          selector: "Literal[value='meta'], Literal[value='token'], Literal[value='final']",
          message: 'Stream event names stay in the StreamEvent union and legacyChatAdapter.',
        },
        {
          selector: 'Literal[value=/var\\(--market-/]',
          message: 'Read var(--market-*) only inside PriceCell and Delta.',
        },
        {
          selector: 'Literal[value=/var\\(--state-/]',
          message: 'Read var(--state-*) only inside StatusBadge.',
        },
        {
          selector: 'Literal[value=/\\[#/]',
          message: 'Arbitrary Tailwind colours stay inside design-system/patterns.',
        },
        {
          selector: 'Literal[value=/\\[var\\(--market-/]',
          message: 'Arbitrary Tailwind colours stay inside design-system/patterns.',
        },
        {
          selector: 'Literal[value=/\\[var\\(--state-/]',
          message: 'Arbitrary Tailwind colours stay inside design-system/patterns.',
        },
      ],
    },
  },
  {
    files: ['src/design-system/patterns/**/*.{js,jsx,ts,tsx}'],
    ignores: ['**/*.test.ts', '**/*.test.tsx'],
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector: "CallExpression[callee.name='fetch']",
          message: 'fetch is allowed only inside platform/api and platform/stream.',
        },
        {
          selector: "NewExpression[callee.name='XMLHttpRequest']",
          message: 'XMLHttpRequest is allowed only inside platform/api and platform/stream.',
        },
        {
          selector: "NewExpression[callee.name='WebSocket']",
          message: 'WebSocket is not allowed.',
        },
        {
          selector: "NewExpression[callee.name='EventSource']",
          message: 'EventSource is not allowed.',
        },
        {
          selector: "Literal[value='meta'], Literal[value='token'], Literal[value='final']",
          message: 'Stream event names stay in the StreamEvent union and legacyChatAdapter.',
        },
        {
          selector: 'Literal[value=/var\\(--market-/]',
          message: 'Read var(--market-*) only inside PriceCell and Delta.',
        },
        {
          selector: 'Literal[value=/var\\(--state-/]',
          message: 'Read var(--state-*) only inside StatusBadge.',
        },
      ],
    },
  },
  {
    files: [
      'src/design-system/patterns/PriceCell/**/*.{js,jsx,ts,tsx}',
      'src/design-system/patterns/Delta/**/*.{js,jsx,ts,tsx}',
    ],
    ignores: ['**/*.test.ts', '**/*.test.tsx'],
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector: "CallExpression[callee.name='fetch']",
          message: 'fetch is allowed only inside platform/api and platform/stream.',
        },
        {
          selector: "NewExpression[callee.name='XMLHttpRequest']",
          message: 'XMLHttpRequest is allowed only inside platform/api and platform/stream.',
        },
        {
          selector: "NewExpression[callee.name='WebSocket']",
          message: 'WebSocket is not allowed.',
        },
        {
          selector: "NewExpression[callee.name='EventSource']",
          message: 'EventSource is not allowed.',
        },
        {
          selector: "Literal[value='meta'], Literal[value='token'], Literal[value='final']",
          message: 'Stream event names stay in the StreamEvent union and legacyChatAdapter.',
        },
        {
          selector: 'Literal[value=/var\\(--state-/]',
          message: 'Read var(--state-*) only inside StatusBadge.',
        },
      ],
    },
  },
  {
    files: ['src/design-system/patterns/StatusBadge/**/*.{js,jsx,ts,tsx}'],
    ignores: ['**/*.test.ts', '**/*.test.tsx'],
    rules: {
      'no-restricted-syntax': [
        'error',
        {
          selector: "CallExpression[callee.name='fetch']",
          message: 'fetch is allowed only inside platform/api and platform/stream.',
        },
        {
          selector: "NewExpression[callee.name='XMLHttpRequest']",
          message: 'XMLHttpRequest is allowed only inside platform/api and platform/stream.',
        },
        {
          selector: "NewExpression[callee.name='WebSocket']",
          message: 'WebSocket is not allowed.',
        },
        {
          selector: "NewExpression[callee.name='EventSource']",
          message: 'EventSource is not allowed.',
        },
        {
          selector: "Literal[value='meta'], Literal[value='token'], Literal[value='final']",
          message: 'Stream event names stay in the StreamEvent union and legacyChatAdapter.',
        },
        {
          selector: 'Literal[value=/var\\(--market-/]',
          message: 'Read var(--market-*) only inside PriceCell and Delta.',
        },
      ],
    },
  },
]
