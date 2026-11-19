import { render, screen, within } from '@testing-library/react'
import { RouterProvider } from 'react-router-dom'
import { beforeEach, describe, expect, it } from 'vitest'
import { AppProviders } from '../providers'
import { t } from '../../platform/i18n/t'
import { createTestRouter } from '../routes'

describe('WorkspaceShell landmarks', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 1920 })
  })

  it('redirects / to /sandbox and exposes four zones', async () => {
    render(
      <AppProviders>
        <RouterProvider router={createTestRouter('/')} />
      </AppProviders>,
    )
    expect(await screen.findByRole('banner', { name: t('shell.zone.z2') })).toBeTruthy()
    const nav = screen.getByRole('navigation', { name: t('shell.zone.z1') })
    const main = screen.getByRole('main', { name: t('shell.zone.z3') })
    const aside = screen.getByRole('complementary', { name: t('shell.zone.z4') })
    expect(nav.getAttribute('data-zone')).toBe('z1')
    expect(screen.getByRole('banner').getAttribute('data-zone')).toBe('z2')
    expect(main.getAttribute('data-zone')).toBe('z3')
    expect(aside.getAttribute('data-zone')).toBe('z4')
    expect(within(nav).getByRole('link', { name: t('shell.track.sandbox') })).toBeTruthy()
    expect(within(nav).getByRole('link', { name: t('shell.track.portfolio') })).toBeTruthy()
    expect(within(nav).getByLabelText(t('shell.z1.lifecycle')).childElementCount).toBe(0)
    expect(within(aside).getByRole('combobox', { name: t('models.select') })).toBeTruthy()
    expect(within(screen.getByRole('banner')).queryByRole('combobox')).toBeNull()
    expect(screen.getByRole('banner').querySelector('[data-panel-resize-handle-id]')).toBeNull()
    expect(nav.querySelectorAll('[data-track-icon]')).toHaveLength(0)
  })

  it('shows a visible track icon for each rail link below 1024 px', async () => {
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 768 })
    render(
      <AppProviders>
        <RouterProvider router={createTestRouter('/sandbox')} />
      </AppProviders>,
    )
    const nav = await screen.findByRole('navigation', { name: t('shell.zone.z1') })
    expect(nav.querySelectorAll('[data-track-icon]')).toHaveLength(2)
    expect(within(nav).getByRole('link', { name: t('shell.track.sandbox') })).toBeTruthy()
    expect(within(nav).getByRole('link', { name: t('shell.track.portfolio') })).toBeTruthy()
  })
})
