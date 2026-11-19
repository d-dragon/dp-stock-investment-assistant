import type { Meta, StoryObj } from '@storybook/react-vite'
import { ZoneFrame, type ZoneState } from './ZoneFrame'

const meta = { component: ZoneFrame } satisfies Meta<typeof ZoneFrame>
export default meta
type Story = StoryObj<typeof meta>

function story(state: ZoneState): Story {
  return { args: { zone: 'z3', state } }
}

export const Empty: Story = story('empty')
export const Loading: Story = story('loading')
export const Ready: Story = story('ready')
export const Stale: Story = story('stale')
export const Error: Story = story('error')
export const Interrupted: Story = story('interrupted')
export const Streaming: Story = story('streaming')
