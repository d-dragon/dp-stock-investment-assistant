import { t } from '../i18n/t'
import { localeSettings } from './localeSettings'

export type NumericInput = number | null | undefined

const MISSING = '—'
const MINUS = '−'

function isMissing(value: NumericInput): value is null | undefined {
  return value === null || value === undefined || Number.isNaN(value)
}

function groupThousands(digits: string): string {
  return digits.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

function fixed(absolute: number, digits: number): string {
  const factor = 10 ** digits
  const rounded = Math.round((absolute + Number.EPSILON) * factor) / factor
  const [whole, fraction = ''] = rounded.toFixed(digits).split('.')
  return `${groupThousands(whole)}.${fraction}`
}

function withSign(value: number, body: string): string {
  if (value === 0) return body
  return value < 0 ? `${MINUS}${body}` : `+${body}`
}

function thousandsOfVnd(value: number): string {
  return fixed(Math.abs(value) / 1000, 2)
}

export const fmt = {
  price(value: NumericInput): string {
    if (isMissing(value)) return MISSING
    const body = thousandsOfVnd(value)
    return value < 0 ? `${MINUS}${body}` : body
  },
  change(value: NumericInput): string {
    if (isMissing(value)) return MISSING
    return withSign(value, thousandsOfVnd(value))
  },
  pct(value: NumericInput): string {
    if (isMissing(value)) return MISSING
    return withSign(value, `${fixed(Math.abs(value) * 100, 2)}%`)
  },
  vnd(value: NumericInput): string {
    if (isMissing(value)) return MISSING
    const body = `${groupThousands(String(Math.round(Math.abs(value))))} ₫`
    return value < 0 ? `${MINUS}${body}` : body
  },
  volume(value: NumericInput): string {
    if (isMissing(value)) return MISSING
    return groupThousands(String(Math.round(Math.abs(value))))
  },
  dateTime(value: Date | string): string {
    const date = value instanceof Date ? value : new Date(value)
    return new Intl.DateTimeFormat(localeSettings.locale, {
      timeZone: localeSettings.timeZone,
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(date)
  },
  missingAccessibleName(): string {
    return t('value.missing')
  },
}
