import { readdirSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { t } from './t'

const here = dirname(fileURLToPath(import.meta.url))

describe('vi-VN catalogue', () => {
  it('returns the launch strings through t()', () => {
    expect(t('stream.retry')).toBe('Tạo lại')
    expect(t('value.missing')).toBe('Không có dữ liệu')
    expect(t('ai.suggested')).toBe('AI gợi ý')
    expect(t('ai.confirmed')).toBe('Đã xác nhận')
    expect(t('app.send')).toBe('Gửi')
    expect(t('app.title')).toBe('Trợ lý đầu tư cổ phiếu DP')
  })

  it('locks the no-JavaScript document strings to the catalogue', () => {
    const html = readFileSync(join(here, '../../../index.html'), 'utf8')
    expect(html).toContain(`<title>${t('app.title')}</title>`)
    expect(html).toContain(`content="${t('app.description')}"`)
    expect(html).toContain(t('app.noscript'))
    expect(html).not.toContain('data-fmt')
  })

  it('ships no English catalogue and no i18n library', () => {
    const names = readdirSync(join(here, 'messages'))
    expect(names.filter((name) => /^en/i.test(name))).toEqual([])
    const pkg = readFileSync(join(here, '../../../package.json'), 'utf8')
    expect(pkg).not.toMatch(/i18next|react-intl|formatjs|lingui/)
  })
})
