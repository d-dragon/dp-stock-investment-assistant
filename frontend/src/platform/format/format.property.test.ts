import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { fmt } from './format'

const here = dirname(fileURLToPath(import.meta.url))

function mulberry32(seed: number): () => number {
  let state = seed
  return () => {
    state += 0x6d2b79f5
    let next = state
    next = Math.imul(next ^ (next >>> 15), next | 1)
    next ^= next + Math.imul(next ^ (next >>> 7), next | 61)
    return ((next ^ (next >>> 14)) >>> 0) / 4294967296
  }
}

function assertSeparators(raw: string): void {
  expect(raw.includes('-')).toBe(false)
  if (raw === '—') return
  const unsigned = raw.replace(/^[+−]/, '').replace(/ ₫$/, '').replace(/%$/, '')
  const pieces = unsigned.split('.')
  expect(pieces.length).toBeLessThanOrEqual(2)
  expect(pieces[0]).toMatch(/^\d{1,3}(,\d{3})*$/)
  if (pieces[1] !== undefined) {
    expect(pieces[1]).toMatch(/^\d+$/)
    expect(pieces[1].includes(',')).toBe(false)
  }
}

describe('fmt separator property', () => {
  it('uses a dot only as a decimal and a comma only as thousands grouping', () => {
    const random = mulberry32(20261117)
    for (let index = 0; index < 1000; index += 1) {
      const whole = Math.floor(random() * 50_000_000)
      const signed = index % 2 === 0 ? whole : -whole
      const ratio = (index % 2 === 0 ? 1 : -1) * random()
      assertSeparators(fmt.price(signed))
      assertSeparators(fmt.change(signed))
      assertSeparators(fmt.pct(ratio))
      assertSeparators(fmt.vnd(Math.abs(whole)))
      const volume = fmt.volume(Math.abs(whole))
      assertSeparators(volume)
      expect(volume.includes('.')).toBe(false)
    }
  })

  it('keeps Intl out of the numeric formatter source', () => {
    const source = readFileSync(join(here, 'format.ts'), 'utf8')
    const numeric = source.slice(0, source.indexOf('dateTime('))
    expect(numeric.includes('Intl')).toBe(false)
  })
})
