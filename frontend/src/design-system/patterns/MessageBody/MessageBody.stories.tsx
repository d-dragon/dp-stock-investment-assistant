import type { Meta, StoryObj } from '@storybook/react-vite'
import { MessageBody } from './MessageBody'

const meta = { component: MessageBody } satisfies Meta<typeof MessageBody>
export default meta
type Story = StoryObj<typeof meta>

export const Ai: Story = {
  args: { body: '**note**', origin: 'ai' },
  render: () => (
    <>
      <MessageBody body="**note**" origin="ai" />
      <MessageBody body="**note**" origin="investor" />
      <MessageBody body={'<img src=x onerror=alert(1)>'} origin="ai" />
    </>
  ),
}
