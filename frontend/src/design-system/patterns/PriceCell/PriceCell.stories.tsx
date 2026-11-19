import type { Meta, StoryObj } from '@storybook/react-vite'
import { PriceCell } from './PriceCell'

const meta = { component: PriceCell } satisfies Meta<typeof PriceCell>
export default meta
type Story = StoryObj<typeof meta>

export const Board: Story = {
  args: { value: 11, reference: 10 },
  render: () => (
    <>
      <PriceCell value={11} reference={10} />
      <PriceCell value={9} reference={10} />
      <PriceCell value={10} reference={10} />
      <PriceCell value={null} />
    </>
  ),
}
