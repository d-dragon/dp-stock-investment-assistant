import { render, screen } from '@testing-library/react'
import { useEffect, useState } from 'react'
import { describe, expect, it } from 'vitest'

function tokenText(body: string): string {
  return body
    .split('\n')
    .filter((line) => line.startsWith('data: {'))
    .map((line) => JSON.parse(line.slice('data: '.length)) as { chunk?: string })
    .map((frame) => frame.chunk ?? '')
    .join('')
}

/** Test-local component. The product shell is not part of this smoke. */
function StreamedChat() {
  const [text, setText] = useState('')

  useEffect(() => {
    let cancelled = false
    void (async () => {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'AAPL', stream: true }),
      })
      const body = await response.text()
      if (!cancelled) {
        setText(tokenText(body))
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  return <p>{text}</p>
}

describe('G1 chat smoke', () => {
  it('renders the streamed token text from the MSW chat frames', async () => {
    render(<StreamedChat />)
    expect(await screen.findByText(/AAPL/)).toBeTruthy()
  })
})
