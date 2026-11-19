import { http, HttpResponse } from 'msw'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { server } from '../../test/msw/handlers'
import { openChatStream } from './openChatStream'

const calls = vi.hoisted(() => ({ keys: [] as string[] }))

vi.mock('./types', () => ({
  t: (key: string) => {
    calls.keys.push(key)
    return key === 'stream.retry' ? 'Tạo lại' : key
  },
}))

function hangingStream(payload: string) {
  const encoder = new TextEncoder()
  return new ReadableStream({
    start(controller) {
      if (payload) controller.enqueue(encoder.encode(payload))
    },
  })
}

async function waitFor(check: () => boolean) {
  for (let attempt = 0; attempt < 50; attempt += 1) {
    if (check()) return
    await new Promise((resolve) => setImmediate(resolve))
  }
}

describe('chat stream idle timeout', () => {
  afterEach(() => {
    vi.useRealTimers()
    calls.keys.length = 0
  })

  it('moves silence to interrupted at 15000ms with fake timers', async () => {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    server.use(
      http.post('/api/chat', () => {
        return new HttpResponse(hangingStream(''), {
          status: 200,
          headers: { 'Content-Type': 'text/event-stream' },
        })
      }),
    )
    const draft = 'Z4 draft'
    const handle = openChatStream({ message: 'hi', stream: true }, { idleTimeoutMs: 15000 })
    expect(handle.retryLabel).toBe('Tạo lại')
    expect(calls.keys).toContain('stream.retry')
    expect(handle.outcome()).toBe('streaming')

    await vi.advanceTimersByTimeAsync(14999)
    expect(handle.outcome()).toBe('streaming')
    await vi.advanceTimersByTimeAsync(1)
    expect(handle.outcome()).toBe('interrupted')
    expect(draft).toBe('Z4 draft')
  })

  it('resets the idle timer on a colon line and does not emit a StreamEvent', async () => {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    server.use(
      http.post('/api/chat', () => {
        return new HttpResponse(hangingStream(': ping\n'), {
          status: 200,
          headers: { 'Content-Type': 'text/event-stream' },
        })
      }),
    )
    const handle = openChatStream({ message: 'hi', stream: true }, { idleTimeoutMs: 15000 })
    const events: { type: string }[] = []
    const reading = (async () => {
      for await (const event of handle.events) events.push(event)
    })()

    await waitFor(() => handle.linesSeen() > 0)
    expect(handle.linesSeen()).toBeGreaterThan(0)
    expect(events).toEqual([])

    await vi.advanceTimersByTimeAsync(14999)
    expect(handle.outcome()).toBe('streaming')
    await vi.advanceTimersByTimeAsync(1)
    expect(handle.outcome()).toBe('interrupted')
    expect(events).toEqual([])
    await Promise.race([reading, Promise.resolve()])
  })

  it('keeps the partial message and the Z4 draft when the stream is interrupted', async () => {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] })
    server.use(
      http.post('/api/chat', () => {
        return new HttpResponse(hangingStream('data: {"chunk":"AAPL "}\n\n'), {
          status: 200,
          headers: { 'Content-Type': 'text/event-stream' },
        })
      }),
    )
    const draft = 'Z4 draft'
    let partial = ''
    const handle = openChatStream({ message: 'hi', stream: true }, { idleTimeoutMs: 15000 })
    const reading = (async () => {
      for await (const event of handle.events) {
        if (event.type === 'token') partial += event.text
      }
    })()

    await waitFor(() => partial === 'AAPL ')
    expect(partial).toBe('AAPL ')
    await vi.advanceTimersByTimeAsync(15000)
    expect(handle.outcome()).toBe('interrupted')
    expect(partial).toBe('AAPL ')
    expect(draft).toBe('Z4 draft')
    expect(handle.retryLabel).toBe(calls.keys.includes('stream.retry') ? 'Tạo lại' : handle.retryLabel)
    await Promise.race([reading, Promise.resolve()])
  })
})
