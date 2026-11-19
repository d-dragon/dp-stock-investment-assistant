import { fmt } from '../../../platform/format/format'

type Band = 'up' | 'down' | 'ref' | 'ceiling' | 'floor'

export interface PriceCellProps {
  value: number | null | undefined
  reference?: number | null
  ceiling?: number | null
  floor?: number | null
}

function bandFor(value: number, reference?: number | null, ceiling?: number | null, floor?: number | null): Band {
  if (ceiling != null && value === ceiling) return 'ceiling'
  if (floor != null && value === floor) return 'floor'
  if (reference != null && value > reference) return 'up'
  if (reference != null && value < reference) return 'down'
  return 'ref'
}

const colour: Record<Band, string> = {
  up: 'var(--market-up)',
  down: 'var(--market-down)',
  ref: 'var(--market-ref)',
  ceiling: 'var(--market-ceiling)',
  floor: 'var(--market-floor)',
}

const arrow: Record<Band, string> = {
  up: '↑',
  down: '↓',
  ref: '',
  ceiling: '',
  floor: '',
}

export function PriceCell({ value, reference, ceiling, floor }: PriceCellProps) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return <span role="img" aria-label={fmt.missingAccessibleName()}>—</span>
  }
  const band = bandFor(value, reference, ceiling, floor)
  return (
    <span role="img" style={{ color: colour[band] }}>
      {arrow[band]}
      {fmt.price(value)}
    </span>
  )
}
