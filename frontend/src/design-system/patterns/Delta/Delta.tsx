import { fmt } from '../../../platform/format/format'
import { t } from '../../../platform/i18n/t'

export interface DeltaProps {
  change: number | null | undefined
  percent?: number | null
}

export function Delta({ change, percent }: DeltaProps) {
  if (change === null || change === undefined || Number.isNaN(change)) {
    return (
      <span role="img" aria-label={t('value.missing')}>
        —
      </span>
    )
  }
  const direction = change > 0 ? 'up' : change < 0 ? 'down' : 'flat'
  const colour =
    direction === 'up' ? 'var(--market-up)' : direction === 'down' ? 'var(--market-down)' : 'var(--market-ref)'
  const arrow = direction === 'up' ? '↑' : direction === 'down' ? '↓' : ''
  const label = direction === 'up' ? t('delta.up') : direction === 'down' ? t('delta.down') : t('delta.flat')
  const percentText =
    percent === null || percent === undefined || Number.isNaN(percent) ? '' : ` ${fmt.pct(percent)}`
  return (
    <span role="img" aria-label={label} style={{ color: colour }}>
      {arrow}
      {fmt.change(change)}
      {percentText}
    </span>
  )
}
