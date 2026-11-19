import { fireEvent, render, screen } from '@testing-library/react'
import { delay, http, HttpResponse } from 'msw'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { t } from '../../platform/i18n/t'
import { server } from '../../test/msw/handlers'
import { Companion } from './Companion'

const ref = { sessionId: 's1', conversationId: 'c1' }

afterEach(() => {
  vi.unstubAllEnvs()
})

describe('companion run', () => {
  it('uses a polite live region and does not send until retry is activated', async () => {
    render(<Companion sessionRef={ref} />)
    expect(document.querySelector('[aria-live="polite"]')).toBeTruthy()
    fireEvent.change(screen.getByRole('textbox', { name: t('app.placeholder') }), { target: { value: 'FPT' } })
    expect(screen.queryByRole('button', { name: t('stream.retry') })).toBeNull()
  })

  it('aborts on stop, keeps the partial, and announces that text once', async () => {
    vi.stubEnv('VITE_STREAM_IDLE_TIMEOUT_MS', '60000')
    let release = () => {}
    const gate = new Promise<void>((resolve) => {
      release = resolve
    })
    server.use(
      http.post('/api/chat', () => {
        const encoder = new TextEncoder()
        const stream = new ReadableStream({
          async start(controller) {
            controller.enqueue(encoder.encode('data: {"chunk":"AA"}\n\n'))
            await gate
            controller.enqueue(encoder.encode('data: {"chunk":"BB"}\n\n'))
            controller.enqueue(encoder.encode('data: [DONE]\n\n'))
            controller.close()
          },
        })
        return new HttpResponse(stream, { headers: { 'Content-Type': 'text/event-stream' } })
      }),
    )
    render(<Companion sessionRef={ref} />)
    fireEvent.change(screen.getByRole('textbox', { name: t('app.placeholder') }), { target: { value: 'FPT' } })
    fireEvent.click(screen.getByRole('button', { name: t('app.send') }))
    expect(await screen.findByText('AA')).toBeTruthy()
    expect(document.querySelector('[aria-live="polite"]')?.textContent ?? '').not.toContain('AA')
    fireEvent.click(screen.getByRole('button', { name: t('app.cancel') }))
    expect(await screen.findByRole('button', { name: t('stream.retry') })).toBeTruthy()
    expect(screen.getByRole('textbox', { name: t('app.placeholder') })).toHaveProperty('value', 'FPT')
    expect(document.querySelector('[aria-live="polite"]')?.textContent ?? '').toContain('AA')
    release()
    await delay(30)
    expect(document.body.textContent ?? '').not.toContain('BB')
  })
})
