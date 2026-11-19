import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { t } from '../../../platform/i18n/t'
import { MessageBody } from './MessageBody'

const fixtures = [
  '<img src=x onerror=alert(1)>',
  '<script>alert(1)</script>',
  '[x](javascript:alert(1))',
  '<a onclick="alert(1)">click</a>',
]

describe('MessageBody', () => {
  it.each(fixtures)('renders %s inert', (body) => {
    const { container } = render(<MessageBody body={body} origin="ai" />)
    expect(container.querySelector('script')).toBeNull()
    expect(container.innerHTML).not.toMatch(/onerror|onclick/i)
    expect(container.querySelector('a[href^="javascript:"]')).toBeNull()
  })

  it('still renders markdown tables, lists, and bold', () => {
    const { container } = render(
      <MessageBody body={'**bold**\n\n- item\n\n| a | b |\n| - | - |\n| 1 | 2 |'} origin="investor" />,
    )
    expect(container.querySelector('strong')).toBeTruthy()
    expect(container.querySelector('li')).toBeTruthy()
    expect(container.querySelector('table')).toBeTruthy()
  })

  it('pairs origin with an edge and a catalogue label', () => {
    const { rerender, container } = render(<MessageBody body="note" origin="ai" />)
    expect(container.querySelector('[data-origin="ai"]')?.getAttribute('style')).toContain('dashed')
    expect(screen.getByText(t('ai.suggested'))).toBeTruthy()
    rerender(<MessageBody body="note" origin="investor" />)
    expect(container.querySelector('[data-origin="investor"]')?.getAttribute('style')).toContain('solid')
    expect(screen.getByText(t('ai.confirmed'))).toBeTruthy()
  })
})
