import type { Decorator, Preview } from '@storybook/react-vite'
import axe from 'axe-core'
import '../src/design-system/tokens/generated/tokens.css'
import '../src/design-system/tokens/generated/fonts.css'

const withTheme: Decorator = (Story) => {
  document.documentElement.setAttribute('data-theme', 'dark')
  document.documentElement.setAttribute('data-density', 'compact')
  return <Story />
}

const preview: Preview = {
  decorators: [withTheme],
  afterEach: async (context) => {
    const root = context.canvasElement ?? document.body
    const results = await axe.run(root)
    const blocking = results.violations.filter((item) => item.impact === 'serious' || item.impact === 'critical')
    if (blocking.length > 0) {
      throw new Error(blocking.map((item) => `${item.id}: ${item.help}`).join('; '))
    }
  },
}

export default preview
