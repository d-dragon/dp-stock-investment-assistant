const config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        surface: 'var(--surface-bg)',
        accent: 'var(--accent)',
      },
    },
  },
}

export default config
