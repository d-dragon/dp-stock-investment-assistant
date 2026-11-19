import type { ReactNode } from 'react'
import { t } from '../../../platform/i18n/t'

export type ZoneState =
  | 'empty'
  | 'loading'
  | 'ready'
  | 'stale'
  | 'error'
  | 'interrupted'
  | 'streaming'

export interface ZoneFrameProps {
  zone?: 'z1' | 'z2' | 'z3' | 'z4'
  state: ZoneState
  children?: ReactNode
  onRetry?: () => void
  onStop?: () => void
}

export function ZoneFrame({ zone, state, children, onRetry, onStop }: ZoneFrameProps) {
  const busy = state === 'loading' || state === 'streaming'
  return (
    <section data-zone={zone} data-state={state} aria-busy={busy ? 'true' : undefined}>
      {state === 'empty' && zone === 'z2' ? <p>{t('shell.z2.emptySymbol')}</p> : null}
      {state === 'ready' || state === 'stale' ? children : null}
      {state === 'error' ? (
        <button type="button" onClick={onRetry}>
          {t('stream.retry')}
        </button>
      ) : null}
      {state === 'interrupted' ? (
        <button type="button" onClick={onRetry}>
          {t('stream.retry')}
        </button>
      ) : null}
      {state === 'streaming' ? (
        <button type="button" onClick={onStop}>
          {t('app.cancel')}
        </button>
      ) : null}
      {state === 'loading' || state === 'empty' ? children : null}
    </section>
  )
}
