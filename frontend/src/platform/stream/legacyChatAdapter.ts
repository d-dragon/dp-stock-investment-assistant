import { ApiError } from '../api/errors'
import { t } from '../i18n/t'
import type { SseFrame, StreamAdapter, StreamEvent } from './types'

function malformed(): StreamEvent[] {
  return [{ type: 'error', error: new ApiError(0, 'malformed_frame', t('stream.malformed'), false) }]
}

export const legacyChatAdapter: StreamAdapter = {
  toEvents(frame: SseFrame): StreamEvent[] | 'end' {
    const data = frame.data.trim()
    if (data === '[DONE]') return 'end'
    let parsed: unknown
    try {
      parsed = JSON.parse(data)
    } catch {
      return malformed()
    }
    if (!parsed || typeof parsed !== 'object') return malformed()
    const record = parsed as Record<string, unknown>
    if ('error' in record) {
      const raw = typeof record.error === 'string' ? record.error : t('stream.fallback')
      const message = /[<>]/.test(raw) ? t('stream.fallback') : raw
      return [{ type: 'error', error: new ApiError(0, 'stream_error', message, false) }]
    }
    if (record.event === 'meta' && typeof record.provider === 'string' && typeof record.model === 'string') {
      return [{ type: 'meta', provider: record.provider, model: record.model }]
    }
    if (typeof record.chunk === 'string') {
      return [{ type: 'token', text: record.chunk }]
    }
    if (record.event === 'done') {
      return [{
        type: 'final',
        provider: typeof record.provider === 'string' ? record.provider : '',
        model: typeof record.model === 'string' ? record.model : '',
        fallback: record.fallback === true,
      }]
    }
    return malformed()
  },
}

type AssistantMessage = {
  content: string
  provider?: string
  model?: string
  fallback?: boolean
  isStreaming?: boolean
}

/** Keeps stream event names in this adapter so callers do not repeat them. */
export function reduceAssistantMessage<T extends AssistantMessage>(message: T, event: StreamEvent): T {
  switch (event.type) {
    case 'meta':
      return { ...message, provider: event.provider, model: event.model }
    case 'token':
      return { ...message, content: message.content + event.text }
    case 'final':
      return {
        ...message,
        isStreaming: false,
        fallback: event.fallback,
        provider: event.provider || message.provider,
        model: event.model || message.model,
      }
    case 'error':
      return {
        ...message,
        isStreaming: false,
        content: `${message.content}\n${t('app.errorPrefix')}: ${event.error.message}`,
      }
    default:
      return message
  }
}
