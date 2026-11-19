import { afterEach, describe, expect, it, vi } from 'vitest'

import { createFakeAuthAdapter } from '../auth/fakeAuthAdapter'
import { createApiClient } from './client'
import { ApiError } from './errors'
import { chatRequestFromSession } from './sessionRef'

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function headerMap(init?: RequestInit): Headers {
  return new Headers(init?.headers)
}

describe('platform API client', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('sends same-origin credentials and no identity headers', async () => {
    const fetchImpl = vi.fn(async (_url: RequestInfo | URL, _init?: RequestInit) => jsonResponse(200, { status: 'ok' }))
    const { auth, stats } = createFakeAuthAdapter()
    const client = createApiClient({ auth, fetchImpl })

    await client.getHealth()

    const [url, init] = fetchImpl.mock.calls[0]
    expect(String(url)).toBe('/api/health')
    expect(init?.credentials).toBe('same-origin')
    expect(init?.method).toBe('GET')
    expect(headerMap(init).get('Authorization')).toBeNull()
    expect(headerMap(init).get('X-User-ID')).toBeNull()
    expect(stats.csrfCalls).toBe(0)
  })

  it('adds csrf headers on POST, PUT, PATCH, and DELETE, including the chat stream', async () => {
    const fetchImpl = vi.fn(async (_url: RequestInfo | URL, _init?: RequestInit) => jsonResponse(200, { ok: true }))
    const { auth, stats } = createFakeAuthAdapter()
    const client = createApiClient({ auth, fetchImpl })

    await client.selectModel({ provider: 'openai', name: 'gpt-4' })
    await client.setDefaultModel('gpt-4')
    await client.request('PATCH', '/api/chat', { message: 'edit' })
    await client.request('DELETE', '/api/chat')
    await client.apiFetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: 'hi', stream: true }),
    })

    expect(stats.csrfCalls).toBe(5)
    for (const [, init] of fetchImpl.mock.calls) {
      expect(init?.credentials).toBe('same-origin')
      const headers = headerMap(init)
      expect(headers.get('X-CSRF-Token')).toBe('fake-csrf')
      expect(headers.get('Authorization')).toBeNull()
      expect(headers.get('X-User-ID')).toBeNull()
    }

    const methods = fetchImpl.mock.calls.map(([, init]) => init?.method)
    expect(methods).toEqual(['POST', 'PUT', 'PATCH', 'DELETE', 'POST'])
    const paths = fetchImpl.mock.calls.map(([url]) => String(url))
    expect(paths).toEqual([
      '/api/models/openai/select',
      '/api/models/openai/default',
      '/api/chat',
      '/api/chat',
      '/api/chat',
    ])
    expect(JSON.parse(String(fetchImpl.mock.calls[1][1]?.body))).toEqual({ model: 'gpt-4' })
    expect(JSON.parse(String(fetchImpl.mock.calls[4][1]?.body))).toEqual({
      message: 'hi',
      stream: true,
    })
  })

  it('calls onUnauthorized on 401 and still throws ApiError', async () => {
    const fetchImpl = vi.fn(async (_url: RequestInfo | URL, _init?: RequestInit) => jsonResponse(401, { message: 'nope' }))
    const { auth, stats } = createFakeAuthAdapter()
    const client = createApiClient({ auth, fetchImpl })

    const error = await client.getHealth().then(
      () => {
        throw new Error('expected ApiError')
      },
      (caught: unknown) => caught,
    )

    expect(stats.unauthorized).toEqual([{ returnTo: window.location.pathname }])
    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({
      status: 401,
      code: 'http_401',
      message: 'nope',
      retriable: false,
    })
  })

  it('maps non-2xx and network failures onto ApiError', async () => {
    const { auth } = createFakeAuthAdapter()
    const cases: Array<{ status: number; body: unknown; code: string; retriable: boolean; message: string }> = [
      { status: 400, body: { code: 'bad_request', message: 'No' }, code: 'bad_request', retriable: false, message: 'No' },
      { status: 429, body: { code: 'rate_limited', message: 'Slow down' }, code: 'rate_limited', retriable: true, message: 'Slow down' },
      { status: 500, body: { message: 'later' }, code: 'http_500', retriable: false, message: 'later' },
      { status: 502, body: {}, code: 'http_502', retriable: true, message: 'http_502' },
      { status: 503, body: {}, code: 'http_503', retriable: true, message: 'http_503' },
      { status: 504, body: {}, code: 'http_504', retriable: true, message: 'http_504' },
    ]

    for (const item of cases) {
      const fetchImpl = vi.fn(async (_url: RequestInfo | URL, _init?: RequestInit) => jsonResponse(item.status, item.body))
      const client = createApiClient({ auth, fetchImpl })
      const error = await client.getConfig().then(
        () => {
          throw new Error('expected ApiError')
        },
        (caught: unknown) => caught,
      )
      expect(error).toBeInstanceOf(ApiError)
      expect(error).toMatchObject({
        status: item.status,
        code: item.code,
        message: item.message,
        retriable: item.retriable,
      })
    }

    const fetchImpl = vi.fn(async (_url: RequestInfo | URL, _init?: RequestInit) => {
      throw new TypeError('Failed to fetch')
    })
    const client = createApiClient({ auth, fetchImpl })
    const network = await client.getHealth().then(
      () => {
        throw new Error('expected ApiError')
      },
      (caught: unknown) => caught,
    )
    expect(network).toBeInstanceOf(ApiError)
    expect(network).toMatchObject({ status: 0, code: 'network', retriable: true })
    expect((network as ApiError).message).not.toMatch(/[<>]/)
  })

  it('does not put raw HTML in ApiError.message', async () => {
    const fetchImpl = vi.fn(async (_url: RequestInfo | URL, _init?: RequestInit) =>
      jsonResponse(400, { code: 'bad', message: '<img src=x onerror=alert(1)>' }),
    )
    const { auth } = createFakeAuthAdapter()
    const client = createApiClient({ auth, fetchImpl })
    const error = await client.getHealth().then(
      () => {
        throw new Error('expected ApiError')
      },
      (caught: unknown) => caught,
    )
    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).message).not.toMatch(/[<>]/)
    expect((error as ApiError).code).toBe('bad')
  })

  it('calls only health, config, models, and chat', async () => {
    const fetchImpl = vi.fn(async (_url: RequestInfo | URL, _init?: RequestInit) => jsonResponse(200, { models: [], source: 'cache' }))
    const { auth } = createFakeAuthAdapter()
    const client = createApiClient({ auth, fetchImpl })

    await client.getHealth()
    await client.getConfig()
    await client.listModels()
    await client.refreshModels()
    await client.getSelectedModel()
    await client.postChat({ message: 'hi' })

    expect(fetchImpl.mock.calls.map(([url, init]) => `${init?.method} ${url}`)).toEqual([
      'GET /api/health',
      'GET /api/config',
      'GET /api/models/openai',
      'POST /api/models/openai/refresh',
      'GET /api/models/openai/selected',
      'POST /api/chat',
    ])
  })

  it('maps conversationId onto conversation_id and omits sessionId', () => {
    const body = chatRequestFromSession(
      { sessionId: 'sess-1', conversationId: 'conv-1' },
      { message: 'hi', stream: true },
    )
    expect(body).toMatchObject({ message: 'hi', stream: true, conversation_id: 'conv-1' })
    expect(body).not.toHaveProperty('session_id')
    expect(JSON.stringify(body)).not.toContain('sess-1')
  })
})
