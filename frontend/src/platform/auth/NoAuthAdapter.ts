import type { AuthAdapter, SessionInfo } from './types'

/** Pitch B adapter. Pitch A replaces this class behind the same interface. */
export class NoAuthAdapter implements AuthAdapter {
  async getSession(): Promise<SessionInfo | null> {
    return null
  }

  csrfHeaders(): Record<string, string> {
    return {}
  }

  signIn(_ctx: { returnTo: string }): void {}

  async signOut(): Promise<void> {}

  async onUnauthorized(_ctx: { returnTo: string }): Promise<void> {}
}
