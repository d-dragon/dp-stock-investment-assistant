import { describe, expect, it } from 'vitest'

import { createFakeAuthAdapter } from './fakeAuthAdapter'
import { NoAuthAdapter } from './NoAuthAdapter'

describe('NoAuthAdapter', () => {
  it('returns no session, no csrf headers, and no-ops the session methods', async () => {
    const adapter = new NoAuthAdapter()

    expect(await adapter.getSession()).toBeNull()
    expect(adapter.csrfHeaders()).toEqual({})
    expect(adapter.signIn({ returnTo: '/workspace' })).toBeUndefined()
    await expect(adapter.signOut()).resolves.toBeUndefined()
    await expect(adapter.onUnauthorized({ returnTo: '/workspace' })).resolves.toBeUndefined()
    expect(adapter).not.toHaveProperty('token')
    expect(sessionStorage.length).toBe(0)
    expect(localStorage.length).toBe(0)
  })

  it('accepts a fake adapter that stores no token', async () => {
    const { auth, stats } = createFakeAuthAdapter()

    expect(await auth.getSession()).toBeNull()
    expect(auth.csrfHeaders()).toEqual({ 'X-CSRF-Token': 'fake-csrf' })
    expect(stats.csrfCalls).toBe(1)
    expect(JSON.stringify(auth)).not.toMatch(/token/i)
    expect(sessionStorage.length).toBe(0)
    expect(localStorage.length).toBe(0)
  })
})
