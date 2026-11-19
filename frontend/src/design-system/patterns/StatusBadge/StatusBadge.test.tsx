import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { StatusBadge } from './StatusBadge'

describe('StatusBadge', () => {
  it('always shows an icon and a label for the given state', () => {
    render(<StatusBadge status="success" label="Đã xác nhận" />)
    const el = screen.getByRole('status')
    expect(el.getAttribute('data-state')).toBe('success')
    expect(el.textContent).toContain('Đã xác nhận')
    expect(el.querySelector('svg')).not.toBeNull()
    expect(el.getAttribute('style') ?? '').toContain('var(--state-success)')
  })
})
