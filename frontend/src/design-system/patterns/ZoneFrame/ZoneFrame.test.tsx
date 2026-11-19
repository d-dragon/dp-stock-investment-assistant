import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { t } from '../../../platform/i18n/t'
import { ZoneFrame, type ZoneState } from './ZoneFrame'

const states: ZoneState[] = ['empty', 'loading', 'ready', 'stale', 'error', 'interrupted', 'streaming']

describe('ZoneFrame', () => {
  it.each(states)('sets data-state for %s', (state) => {
    render(<ZoneFrame zone="z3" state={state} />)
    expect(document.querySelector('section')?.getAttribute('data-state')).toBe(state)
  })

  it('marks loading and streaming busy', () => {
    const { rerender } = render(<ZoneFrame state="loading" />)
    expect(document.querySelector('section')?.getAttribute('aria-busy')).toBe('true')
    rerender(<ZoneFrame state="streaming" />)
    expect(document.querySelector('section')?.getAttribute('aria-busy')).toBe('true')
  })

  it('shows the empty symbol on Z2', () => {
    render(<ZoneFrame zone="z2" state="empty" />)
    expect(screen.getByText(t('shell.z2.emptySymbol'))).toBeTruthy()
  })

  it('does not request anything while interrupted until retry is activated', async () => {
    vi.useFakeTimers()
    const fetchSpy = vi.spyOn(globalThis, 'fetch')
    const onRetry = vi.fn()
    render(<ZoneFrame state="interrupted" onRetry={onRetry} />)
    await vi.advanceTimersByTimeAsync(5000)
    expect(fetchSpy).not.toHaveBeenCalled()
    expect(onRetry).not.toHaveBeenCalled()
    vi.useRealTimers()
    fireEvent.click(screen.getByRole('button', { name: t('stream.retry') }))
    expect(onRetry).toHaveBeenCalledOnce()
  })
})
