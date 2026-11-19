import { describe, expect, it } from 'vitest'

import { ApiError } from '../api/errors'
import { legacyChatAdapter } from './legacyChatAdapter'
import { parseSse } from './parseSse'

describe('legacyChatAdapter', () => {
  it('keeps WHATWG id, event, and retry on the parsed frame', () => {
    expect(parseSse('id: 7\nevent: message\nretry: 3000\ndata: {"chunk":"A"}\n\n')).toEqual([
      { id: '7', event: 'message', retry: 3000, data: '{"chunk":"A"}' },
    ])
  })

  it('maps today frames to meta, token, final, and end', () => {
    expect(
      legacyChatAdapter.toEvents({ data: '{"event":"meta","provider":"openai","model":"gpt-4"}' }),
    ).toEqual([{ type: 'meta', provider: 'openai', model: 'gpt-4' }])
    expect(legacyChatAdapter.toEvents({ data: '{"chunk":"AAPL "}' })).toEqual([
      { type: 'token', text: 'AAPL ' },
    ])
    expect(
      legacyChatAdapter.toEvents({
        data: '{"event":"done","fallback":false,"provider":"openai","model":"gpt-4"}',
      }),
    ).toEqual([{ type: 'final', provider: 'openai', model: 'gpt-4', fallback: false }])
    expect(legacyChatAdapter.toEvents({ data: '[DONE]' })).toBe('end')
  })

  it('turns an error object or a malformed frame into an error event', () => {
    const errored = legacyChatAdapter.toEvents({ data: '{"error":"nope"}' })
    expect(errored).not.toBe('end')
    if (errored === 'end') return
    expect(errored[0]?.type).toBe('error')
    if (errored[0]?.type === 'error') {
      expect(errored[0].error).toBeInstanceOf(ApiError)
    }

    const malformed = legacyChatAdapter.toEvents({ data: '{oops' })
    expect(malformed).not.toBe('end')
    if (malformed === 'end') return
    expect(malformed[0]?.type).toBe('error')
  })

  it('does not dispatch a colon comment as a frame', () => {
    expect(parseSse(': ping\n\n')).toEqual([])
  })
})
