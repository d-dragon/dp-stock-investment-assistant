import { describe, expect, it } from 'vitest'
import { parseSymbol, parseTrack } from './routeParams'

describe('route params', () => {
  it('accepts only the two tracks', () => {
    expect(parseTrack('sandbox')).toBe('sandbox')
    expect(parseTrack('portfolio')).toBe('portfolio')
    expect(parseTrack('Sandbox')).toBeNull()
    expect(parseTrack('other')).toBeNull()
  })

  it('accepts the sample symbols and rejects lowercase', () => {
    expect(parseSymbol('FPT')).toBe('FPT')
    expect(parseSymbol('VNINDEX')).toBe('VNINDEX')
    expect(parseSymbol('VN30')).toBe('VN30')
    expect(parseSymbol('fpt')).toBeNull()
    expect(parseSymbol('')).toBeNull()
  })
})
