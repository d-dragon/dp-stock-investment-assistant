export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly retriable: boolean

  constructor(status: number, code: string, message: string, retriable: boolean) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.retriable = retriable
  }
}

export function isRetriableStatus(status: number): boolean {
  return status === 0 || status === 429 || (status >= 502 && status <= 504)
}

/** Drop markup so a backend message cannot render as HTML. */
export function safeMessage(value: unknown, fallback: string): string {
  if (typeof value !== 'string') return fallback
  const trimmed = value.trim()
  if (!trimmed || /[<>]/.test(trimmed)) return fallback
  return trimmed
}
