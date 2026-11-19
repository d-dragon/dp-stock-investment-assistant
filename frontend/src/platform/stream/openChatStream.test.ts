import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { http, HttpResponse } from 'msw'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { server } from '../../test/msw/handlers'
import { openChatStream } from './openChatStream'

const frames = [
  'data: {"event":"meta","provider":"openai","model":"gpt-4"}',
  '',
  'data: {"chunk":"AAPL "}',
  '',
  'data: {"event":"done","fallback":false,"provider":"openai","model":"gpt-4"}',
  '',
  'data: [DONE]',
  '',
].join('\n')

async function collect(handle: ReturnType<typeof openChatStream>) {
  const events = []
  for await (const event of handle.events) {
    events.push(event)
  }
  return events
}

describe('openChatStream', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllEnvs()
  })

  it('posts the chat stream with same-origin credentials and adapts today frames', async () => {
    server.use(
      http.post('/api/chat', () => {
        return new HttpResponse(frames, {
          status: 200,
          headers: { 'Content-Type': 'text/event-stream' },
        })
      }),
    )
    const fetchSpy = vi.spyOn(globalThis, 'fetch')
    const handle = openChatStream({ message: 'AAPL', stream: true }, { idleTimeoutMs: 60000 })
    const events = await collect(handle)

    expect(events.map((event) => event.type)).toEqual(['meta', 'token', 'final'])
    expect(handle.outcome()).toBe('ended')
    const init = fetchSpy.mock.calls.at(-1)?.[1] as RequestInit
    expect(init.credentials).toBe('same-origin')
    expect(init.method).toBe('POST')
    const body = JSON.parse(String(init.body)) as { stream?: boolean; session_id?: string }
    expect(body.stream).toBe(true)
    expect(body).not.toHaveProperty('session_id')
    expect(String(fetchSpy.mock.calls.at(-1)?.[0])).toContain('/api/chat')
  })

  it('yields an error event for an error frame and for a malformed frame', async () => {
    server.use(
      http.post('/api/chat', () => {
        return new HttpResponse('data: {"error":"nope"}\n\n', {
          status: 200,
          headers: { 'Content-Type': 'text/event-stream' },
        })
      }),
    )
    const errored = openChatStream({ message: 'x', stream: true }, { idleTimeoutMs: 60000 })
    const errorEvents = await collect(errored)
    expect(errorEvents.map((event) => event.type)).toEqual(['error'])
    expect(errored.outcome()).toBe('error')

    server.use(
      http.post('/api/chat', () => {
        return new HttpResponse('data: {oops\n\n', {
          status: 200,
          headers: { 'Content-Type': 'text/event-stream' },
        })
      }),
    )
    const malformed = openChatStream({ message: 'x', stream: true }, { idleTimeoutMs: 60000 })
    const malformedEvents = await collect(malformed)
    expect(malformedEvents.map((event) => event.type)).toEqual(['error'])
    expect(malformed.outcome()).toBe('error')
  })

  it('aborts the first chat stream when a second one opens in the tab', () => {
    const first = openChatStream({ message: 'one', stream: true }, { idleTimeoutMs: 60000 })
    const second = openChatStream({ message: 'two', stream: true }, { idleTimeoutMs: 60000 })
    expect(first.outcome()).toBe('aborted')
    second.abort()
    expect(second.outcome()).toBe('aborted')
  })

  it('reads the live idle window from Vite env and does not substitute 60000', () => {
    const source = readFileSync(join(dirname(fileURLToPath(import.meta.url)), 'openChatStream.ts'), 'utf8')
    expect(source).not.toMatch(/\b60000\b/)
    vi.stubEnv('VITE_STREAM_IDLE_TIMEOUT_MS', '')
    expect(() => openChatStream({ message: 'x', stream: true })).toThrow(/VITE_STREAM_IDLE_TIMEOUT_MS/)
  })
})
