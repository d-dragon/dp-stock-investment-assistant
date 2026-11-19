export type TrackId = 'sandbox' | 'portfolio'

export function parseTrack(segment: string | undefined): TrackId | null {
  if (segment === 'sandbox' || segment === 'portfolio') return segment
  return null
}

/** Accepts a non-empty segment with no lowercase letter. No extra character class. */
export function parseSymbol(segment: string | undefined): string | null {
  if (!segment) return null
  if ([...segment].some((char) => char >= 'a' && char <= 'z')) return null
  return segment
}

export interface ParsedPath {
  track: TrackId | null
  symbol: string | null
  notFound: boolean
}

export function parsePathname(pathname: string): ParsedPath {
  const parts = pathname.split('/').filter(Boolean)
  if (parts.length === 0) {
    return { track: 'sandbox', symbol: null, notFound: false }
  }
  const track = parseTrack(parts[0])
  if (!track) return { track: null, symbol: null, notFound: true }
  if (parts.length === 1) return { track, symbol: null, notFound: false }
  if (parts.length > 2) return { track: null, symbol: null, notFound: true }
  const symbol = parseSymbol(parts[1])
  if (!symbol) return { track: null, symbol: null, notFound: true }
  return { track, symbol, notFound: false }
}

export function showsAccessNotFound(status: number): boolean {
  return status === 404 || status === 403
}
