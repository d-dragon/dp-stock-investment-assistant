import type { SseFrame } from './types'

export interface SseParser {
  push(chunk: string): SseFrame[]
}

export function createSseParser(): SseParser {
  let buffer = ''
  let eventName = ''
  let id: string | undefined
  let retry: number | undefined
  const data: string[] = []

  const reset = () => {
    eventName = ''
    id = undefined
    retry = undefined
    data.length = 0
  }

  return {
    push(chunk: string): SseFrame[] {
      buffer += chunk
      const frames: SseFrame[] = []
      while (true) {
        const breakAt = buffer.indexOf('\n')
        if (breakAt < 0) break
        let line = buffer.slice(0, breakAt)
        buffer = buffer.slice(breakAt + 1)
        if (line.endsWith('\r')) line = line.slice(0, -1)
        if (line === '') {
          const hasField = data.length > 0 || eventName !== '' || id !== undefined || retry !== undefined
          if (hasField) {
            const frame: SseFrame = { data: data.join('\n') }
            if (id !== undefined) frame.id = id
            if (eventName !== '') frame.event = eventName
            if (retry !== undefined) frame.retry = retry
            frames.push(frame)
          }
          reset()
          continue
        }
        if (line.startsWith(':')) continue
        const colon = line.indexOf(':')
        const field = colon >= 0 ? line.slice(0, colon) : line
        let value = colon >= 0 ? line.slice(colon + 1) : ''
        if (value.startsWith(' ')) value = value.slice(1)
        if (field === 'data') data.push(value)
        else if (field === 'event') eventName = value
        else if (field === 'id') id = value
        else if (field === 'retry' && /^\d+$/.test(value)) retry = Number(value)
      }
      return frames
    },
  }
}

export function parseSse(text: string): SseFrame[] {
  const parser = createSseParser()
  return parser.push(text.endsWith('\n') ? text : `${text}\n`)
}
