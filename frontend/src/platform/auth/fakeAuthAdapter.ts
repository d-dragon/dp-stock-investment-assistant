import type { AuthAdapter } from './types'

/**
 * Test double for AuthAdapter. Holds no token and touches no storage.
 * Production code ships NoAuthAdapter; tests pass this fake in.
 */
export function createFakeAuthAdapter(): {
  auth: AuthAdapter
  stats: { csrfCalls: number; unauthorized: { returnTo: string }[] }
} {
  const stats = { csrfCalls: 0, unauthorized: [] as { returnTo: string }[] }
  const auth: AuthAdapter = {
    async getSession() {
      return null
    },
    csrfHeaders() {
      stats.csrfCalls += 1
      return { 'X-CSRF-Token': 'fake-csrf' }
    },
    signIn() {},
    async signOut() {},
    async onUnauthorized(ctx) {
      stats.unauthorized.push({ returnTo: ctx.returnTo })
    },
  }
  return { auth, stats }
}
