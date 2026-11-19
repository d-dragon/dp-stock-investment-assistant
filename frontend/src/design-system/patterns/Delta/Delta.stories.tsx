import type { Meta, StoryObj } from '@storybook/react-vite'
import { Delta } from './Delta'

const meta = { component: Delta } satisfies Meta<typeof Delta>
export default meta
type Story = StoryObj<typeof meta>

export const Up: Story = {
  args: { change: 1, percent: 0.1 },
  render: () => (
    <>
      <Delta change={1} percent={0.1} />
      <Delta change={-1} percent={-0.1} />
      <Delta change={0} percent={0} />
      <Delta change={null} />
    </>
  ),
}
