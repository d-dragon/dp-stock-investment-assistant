import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { AppProviders } from './app/providers'
import { createAppRouter } from './app/routes'
import './design-system/tokens/generated/tokens.css'
import './design-system/tokens/generated/fonts.css'

const container = document.getElementById('root')
if (!container) {
  throw new Error('Missing #root')
}

async function boot(): Promise<void> {
  if (import.meta.env.VITE_USE_MOCKS === 'true') {
    const { startBrowserMocks } = await import('./mocks/browser')
    await startBrowserMocks()
  }
  createRoot(container!).render(
    <StrictMode>
      <AppProviders>
        <RouterProvider router={createAppRouter()} />
      </AppProviders>
    </StrictMode>,
  )
}

void boot()
