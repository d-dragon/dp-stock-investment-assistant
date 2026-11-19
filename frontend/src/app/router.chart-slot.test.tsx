import { render, screen, waitFor } from '@testing-library/react'
import { RouterProvider } from 'react-router-dom'
import { beforeEach, describe, expect, it } from 'vitest'
import { AppProviders } from './providers'
import { t } from '../platform/i18n/t'
import { createTestRouter } from './routes'

function renderAt(path: string, accessStatus?: number) {
  return render(
    <AppProviders>
      <RouterProvider router={createTestRouter(path, accessStatus)} />
    </AppProviders>,
  )
}

describe('chart slot and not-found', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 1920 })
  })

  it('shows an empty slot on sandbox and none on portfolio', async () => {
    const sandbox = renderAt('/sandbox')
    expect(await screen.findByRole('main')).toBeTruthy()
    await waitFor(() => {
      expect(document.querySelector('[data-chart-slot]')).toBeTruthy()
    })
    expect(screen.getByText(t('shell.z3.emptyInvitation'))).toBeTruthy()
    sandbox.unmount()

    renderAt('/portfolio')
    expect(await screen.findByRole('main')).toBeTruthy()
    await waitFor(() => {
      expect(document.querySelector('[data-track-ready]')).toBeTruthy()
    })
    expect(document.querySelector('[data-chart-slot]')).toBeNull()
  })

  it('keeps the shell around unknown, lowercase, and access failures', async () => {
    for (const path of ['/nope', '/sandbox/fpt', '/missing/extra/parts']) {
      const view = renderAt(path)
      expect(await screen.findByText(t('shell.notFound'))).toBeTruthy()
      expect(screen.getByRole('banner')).toBeTruthy()
      expect(screen.getByRole('navigation')).toBeTruthy()
      view.unmount()
    }
    const denied = renderAt('/sandbox', 404)
    expect(await screen.findByText(t('shell.notFound'))).toBeTruthy()
    denied.unmount()
    renderAt('/sandbox', 403)
    expect(await screen.findByText(t('shell.notFound'))).toBeTruthy()
  })
})
