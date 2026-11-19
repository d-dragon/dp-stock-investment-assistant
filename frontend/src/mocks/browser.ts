import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

export async function startBrowserMocks(): Promise<void> {
  const worker = setupWorker(...handlers)
  await worker.start({ onUnhandledRequest: 'bypass', quiet: true })
  document.documentElement.dataset.mocks = 'on'
}
