import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it, vi } from 'vitest'

import { createFakeAuthAdapter } from '../auth/fakeAuthAdapter'
import { createApiClient } from './client'

describe('platform API client scope', () => {
  it('does not call the market price path', async () => {
    const fetchImpl = vi.fn(async () => new Response('{}', { status: 200 }))
    const { auth } = createFakeAuthAdapter()
    const client = createApiClient({ auth, fetchImpl })

    await expect(client.request('GET', '/api/market/prices/FPT')).rejects.toThrow(/not allowed/)
    expect(fetchImpl).not.toHaveBeenCalled()
  })

  it('does not mention the market price path in the client source', () => {
    const source = readFileSync(join(dirname(fileURLToPath(import.meta.url)), 'client.ts'), 'utf8')
    expect(source).not.toContain('/api/market/prices')
  })
})
