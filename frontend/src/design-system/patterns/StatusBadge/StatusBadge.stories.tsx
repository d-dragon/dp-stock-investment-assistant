import type { Meta, StoryObj } from '@storybook/react-vite'
import { StatusBadge } from './StatusBadge'

const meta = { component: StatusBadge } satisfies Meta<typeof StatusBadge>
export default meta
type Story = StoryObj<typeof meta>

export const Info: Story = {
  args: { status: 'info', label: 'zero' },
  render: () => (
    <>
      <StatusBadge status="success" label="up" />
      <StatusBadge status="danger" label="down" />
      <StatusBadge status="info" label="zero" />
      <StatusBadge status="warn" label="missing" />
    </>
  ),
}
