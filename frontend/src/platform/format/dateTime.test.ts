import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it, vi } from 'vitest'
import { fmt } from './format'
import { localeSettings } from './localeSettings'

const here = dirname(fileURLToPath(import.meta.url))

describe('fmt.dateTime', () => {
  it('uses Intl with the launch locale and time zone settings', () => {
    expect(localeSettings.locale).toBe('vi-VN')
    expect(localeSettings.timeZone).toBe('Asia/Ho_Chi_Minh')
    const dateTimeFormat = vi.spyOn(Intl, 'DateTimeFormat')
    fmt.dateTime('2026-11-17T03:30:00Z')
    expect(dateTimeFormat).toHaveBeenCalled()
    const [locale, options] = dateTimeFormat.mock.calls[0]
    expect(locale).toBe(localeSettings.locale)
    expect(options).toMatchObject({ timeZone: localeSettings.timeZone })
    dateTimeFormat.mockRestore()
  })

  it('does not bury the locale or time zone inside the dateTime call', () => {
    const source = readFileSync(join(here, 'format.ts'), 'utf8')
    const body = source.slice(source.indexOf('dateTime('))
    expect(body.includes("'vi-VN'")).toBe(false)
    expect(body.includes('"vi-VN"')).toBe(false)
    expect(body.includes('Asia/Ho_Chi_Minh')).toBe(false)
  })
})
