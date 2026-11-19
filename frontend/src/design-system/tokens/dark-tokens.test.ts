import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { darkTokens, lightHexes } from './dark-palette.fixture'

const css = readFileSync(
  join(dirname(fileURLToPath(import.meta.url)), 'generated', 'tokens.css'),
  'utf8',
)

describe('dark tokens', () => {

  it('matches the copied dark column, including --market-up', () => {
    expect(css).toMatch(/--market-up\s*:\s*#2EBD6B/i)
    for (const [id, hex] of Object.entries(darkTokens)) {
      const variable = `--${id.replaceAll('.', '-')}`
      expect(css).toMatch(new RegExp(`${variable}\\s*:\\s*${hex}`, 'i'))
    }
  })

  it('emits two-part variables only and omits light, track, and zone aliases', () => {
    const upper = css.toUpperCase()
    for (const hex of lightHexes) {
      expect(upper.includes(hex.toUpperCase())).toBe(false)
    }
    expect(css).not.toMatch(/--track-a\b|--track-b\b|--surface-z[1-4]\b|--surface-overlay\b|--ai-/i)
    const names = [...css.matchAll(/--([a-z0-9-]+)\s*:/gi)].map((match) => match[1])
    expect(names.length).toBeGreaterThan(0)
    for (const name of names) {
      expect(name.split('-').length).toBeLessThanOrEqual(2)
    }
  })
})
