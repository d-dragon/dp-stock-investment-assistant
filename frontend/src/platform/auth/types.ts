export interface SessionInfo {
  userId: string
  displayName?: string
  expiresAt: string
}

export interface AuthAdapter {
  getSession(): Promise<SessionInfo | null>
  csrfHeaders(): Record<string, string>
  signIn(ctx: { returnTo: string }): void
  signOut(): Promise<void>
  onUnauthorized(ctx: { returnTo: string }): Promise<void>
}
