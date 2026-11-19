import type { ApiError } from '../api/errors'

export type StreamEvent =
  | { type: 'meta'; provider: string; model: string }
  | { type: 'token'; text: string }
  | { type: 'final'; provider: string; model: string; fallback: boolean }
  | { type: 'error'; error: ApiError }

export interface SseFrame {
  id?: string
  event?: string
  retry?: number
  data: string
}

export interface StreamAdapter {
  toEvents(frame: SseFrame): StreamEvent[] | 'end'
}

export type StreamOutcome = 'streaming' | 'interrupted' | 'error' | 'ended' | 'aborted'

export interface StreamHandle {
  events: AsyncIterable<StreamEvent>
  abort(): void
  outcome(): StreamOutcome
  retryLabel: string
  linesSeen(): number
}

export { t } from '../i18n'
