import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { chatSseFrames } from './chat-frames'

export const handlers = [
  http.post('/api/chat', () => {
    return new HttpResponse(chatSseFrames, {
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' },
    })
  }),
]

export const server = setupServer(...handlers)
