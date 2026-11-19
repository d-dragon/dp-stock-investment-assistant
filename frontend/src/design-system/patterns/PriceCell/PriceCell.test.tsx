import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { PriceCell } from './PriceCell'

describe('PriceCell', () => {
  it('colours from the supplied reference, ceiling, and floor', () => {
    const { rerender } = render(
      <PriceCell value={110000} reference={100000} ceiling={999999} floor={1} />,
    )
    expect(screen.getByRole('img').getAttribute('style') ?? '').toContain('var(--market-up)')
    expect(screen.getByRole('img').textContent ?? '').toMatch(/[+\u2212↑↓▲▼]/)

    rerender(<PriceCell value={50000} reference={100000} ceiling={999999} floor={1} />)
    expect(screen.getByRole('img').getAttribute('style') ?? '').toContain('var(--market-down)')

    rerender(<PriceCell value={999999} reference={100000} ceiling={999999} floor={1} />)
    expect(screen.getByRole('img').getAttribute('style') ?? '').toContain('var(--market-ceiling)')

    rerender(<PriceCell value={1} reference={100000} ceiling={999999} floor={1} />)
    expect(screen.getByRole('img').getAttribute('style') ?? '').toContain('var(--market-floor)')

    rerender(<PriceCell value={100000} reference={100000} ceiling={999999} floor={1} />)
    const flat = screen.getByRole('img')
    expect(flat.getAttribute('style') ?? '').toContain('var(--market-ref)')
    expect(flat.textContent ?? '').not.toMatch(/[+\u2212↑↓▲▼]/)
  })

  it('shows 0.00 in market.ref when the price is zero and does not invent a band', () => {
    render(<PriceCell value={0} reference={0} ceiling={999999} floor={1} />)
    const el = screen.getByRole('img')
    expect(el.textContent).toContain('0.00')
    expect(el.textContent ?? '').not.toMatch(/[+\u2212]/)
    expect(el.getAttribute('style') ?? '').toContain('var(--market-ref)')
    const source = readFileSync(join(dirname(fileURLToPath(import.meta.url)), 'PriceCell.tsx'), 'utf8')
    expect(source).not.toMatch(/0\.07|1\.07|HOSE|HNX|UPCoM/)
  })

  it('shows an em dash when the value is missing', () => {
    render(<PriceCell value={null} reference={100000} ceiling={110000} floor={90000} />)
    expect(screen.getByRole('img').textContent).toContain('—')
  })
})
