import { getApiClient } from '../api/client'
import { ApiError } from '../api/errors'
import type { ChatRequestFields } from '../api/sessionRef'
import { legacyChatAdapter } from './legacyChatAdapter'
import { createSseParser } from './parseSse'
import { t } from './types'
import type { StreamEvent, StreamHandle, StreamOutcome } from './types'

interface ActiveStream {
  abort: () => void
}

let active: ActiveStream | null = null

function defaultIdleMs(): number {
  const parsed = Number(import.meta.env.VITE_STREAM_IDLE_TIMEOUT_MS)
  if (!Number.isFinite(parsed) || parsed <= 0) {
    throw new Error('VITE_STREAM_IDLE_TIMEOUT_MS must be a positive number of milliseconds')
  }
  return parsed
}

function isAbortError(err: unknown): boolean {
  return (err instanceof DOMException || err instanceof Error) && err.name === 'AbortError'
}

export function openChatStream(
  body: ChatRequestFields,
  opts?: { signal?: AbortSignal; idleTimeoutMs?: number },
): StreamHandle {
  active?.abort()

  let outcome: StreamOutcome = 'streaming'
  let lines = 0
  let reader: ReadableStreamDefaultReader<string> | undefined
  const controller = new AbortController()
  const idleMs = opts?.idleTimeoutMs ?? defaultIdleMs()
  let timer: ReturnType<typeof setTimeout> | undefined

  const clearIdle = () => {
    if (timer !== undefined) {
      clearTimeout(timer)
      timer = undefined
    }
  }

  const arm = () => {
    clearIdle()
    timer = setTimeout(() => {
      if (outcome !== 'streaming') return
      outcome = 'interrupted'
      void reader?.cancel().catch(() => undefined)
      controller.abort()
    }, idleMs)
  }

  const abort = () => {
    if (outcome === 'streaming') outcome = 'aborted'
    clearIdle()
    void reader?.cancel().catch(() => undefined)
    controller.abort()
  }

  active = { abort }
  arm()

  if (opts?.signal) {
    if (opts.signal.aborted) abort()
    else opts.signal.addEventListener('abort', () => abort(), { once: true })
  }

  const events: AsyncIterable<StreamEvent> = {
    async *[Symbol.asyncIterator]() {
      const parser = createSseParser()
      try {
        const response = await getApiClient().apiFetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'text/event-stream',
          },
          body: JSON.stringify({ ...body, stream: true }),
        })
        if (!response.body) {
          throw new ApiError(0, 'stream_unsupported', 'Streaming is not supported', false)
        }
        const bodyReader = response.body.pipeThrough(new TextDecoderStream()).getReader()
        reader = bodyReader
        let rest = ''

        const takeFrames = function* (chunk: string): Generator<StreamEvent> {
          for (const frame of parser.push(chunk)) {
            const adapted = legacyChatAdapter.toEvents(frame)
            if (adapted === 'end') {
              outcome = 'ended'
              return
            }
            for (const event of adapted) {
              if (event.type === 'error') outcome = 'error'
              yield event
            }
          }
        }

        while (outcome === 'streaming') {
          const { done, value } = await bodyReader.read()
          const chunk = done ? `${rest}\n` : `${rest}${value ?? ''}`
          const parts = chunk.split('\n')
          rest = done ? '' : (parts.pop() ?? '')
          for (const line of parts) {
            if (outcome !== 'streaming') break
            lines += 1
            arm()
            for (const event of takeFrames(`${line}\n`)) {
              yield event
              if (outcome !== 'streaming') break
            }
          }
          if (done) {
            if (outcome === 'streaming') outcome = 'ended'
            break
          }
        }
        clearIdle()
      } catch (err) {
        if (outcome !== 'streaming') return
        outcome = 'error'
        if (isAbortError(err)) return
        const error = err instanceof ApiError
          ? err
          : new ApiError(0, 'network', 'network', true)
        yield { type: 'error', error }
      } finally {
        clearIdle()
        if (active?.abort === abort) active = null
      }
    },
  }

  return {
    events,
    abort,
    outcome: () => outcome,
    retryLabel: t('stream.retry'),
    linesSeen: () => lines,
  }
}
