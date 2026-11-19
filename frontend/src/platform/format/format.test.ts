import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it, vi } from 'vitest'
import { fmt } from './format'

const here = dirname(fileURLToPath(import.meta.url))

const MISSING = ['—', 'Không có dữ liệu'] as const

describe('fmt board numbers', () => {
  it('locks the pitch rows', () => {
    expect(fmt.price(25300)).toBe('25.30')
    expect(fmt.pct(0.0698)).toBe('+6.98%')
    expect(fmt.volume(1234500)).toBe('1,234,500')
    expect(fmt.vnd(25300000)).toBe('25,300,000 ₫')
    expect(fmt.change(1750)).toBe('+1.75')
    expect(fmt.change(-450)).toBe('−0.45')
    expect(fmt.pct(-0.0698)).toBe('−6.98%')
    expect(fmt.change(0)).toBe('0.00')
    expect(fmt.pct(0)).toBe('0.00%')
    expect(fmt.volume(0)).toBe('0')
  })

  it('renders missing numbers as an em dash with the catalogue accessible name', () => {
    for (const value of [null, undefined, Number.NaN]) {
      expect(fmt.price(value)).toBe(MISSING[0])
      expect(fmt.change(value)).toBe(MISSING[0])
      expect(fmt.pct(value)).toBe(MISSING[0])
      expect(fmt.vnd(value)).toBe(MISSING[0])
      expect(fmt.volume(value)).toBe(MISSING[0])
      expect(fmt.missingAccessibleName()).toBe(MISSING[1])
    }
  })

  it('does not use Intl for numeric formatters', () => {
    const numberFormat = vi.spyOn(Intl, 'NumberFormat')
    fmt.price(25300)
    fmt.change(-450)
    fmt.pct(-0.0698)
    fmt.vnd(25300000)
    fmt.volume(0)
    expect(numberFormat).not.toHaveBeenCalled()
    numberFormat.mockRestore()
  })

  it('keeps volume off the price formatter', () => {
    const source = readFileSync(join(here, 'format.ts'), 'utf8')
    const volumeStart = source.indexOf('volume(')
    const dateStart = source.indexOf('dateTime(')
    const volumeBody = source.slice(volumeStart, dateStart)
    expect(volumeBody).not.toMatch(/price\s*\(/)
    expect(volumeBody).not.toMatch(/Intl/)
  })
})
