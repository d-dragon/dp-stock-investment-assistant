import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { t } from '../../../platform/i18n/t'
import { Delta } from './Delta'

describe('Delta', () => {
  it('shows a sign or an arrow with colour, and names the direction from t()', () => {
    const up = t('delta.up')
    const down = t('delta.down')
    const flat = t('delta.flat')
    expect(up.length).toBeGreaterThan(0)
    expect(down.length).toBeGreaterThan(0)
    expect(flat.length).toBeGreaterThan(0)
    expect(new Set([up, down, flat]).size).toBe(3)

    const { rerender } = render(<Delta change={1750} percent={0.0698} />)
    let el = screen.getByRole('img')
    expect(el.textContent ?? '').toMatch(/\+|↑|▲/)
    expect(el.getAttribute('style') ?? '').toContain('var(--market-up)')
    expect(el.getAttribute('aria-label')).toBe(up)

    rerender(<Delta change={-450} percent={-0.0698} />)
    el = screen.getByRole('img')
    expect(el.textContent ?? '').toMatch(/−|↓|▼/)
    expect(el.getAttribute('style') ?? '').toContain('var(--market-down)')
    expect(el.getAttribute('aria-label')).toBe(down)
  })

  it('shows an unsigned zero in market.ref', () => {
    render(<Delta change={0} percent={0} />)
    const el = screen.getByRole('img')
    expect(el.textContent).toContain('0.00')
    expect(el.textContent).toContain('0.00%')
    expect(el.textContent ?? '').not.toMatch(/[+\u2212↑↓▲▼]/)
    expect(el.getAttribute('style') ?? '').toContain('var(--market-ref)')
    expect(el.getAttribute('aria-label')).toBe(t('delta.flat'))
  })

  it('shows an em dash when the change is missing', () => {
    render(<Delta change={null} />)
    expect(screen.getByRole('img').textContent).toContain('—')
  })
})
