import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { handlers as shared } from '../mocks/handlers'
import { handlers as fromTest } from './msw/handlers'

const frontend = join(dirname(fileURLToPath(import.meta.url)), '../..')

describe('MSW handler set', () => {
  it('shares one module across Vitest and the browser list', () => {
    expect(fromTest).toBe(shared)
    const source = readFileSync(join(frontend, 'src/mocks/handlers.ts'), 'utf8')
    for (const path of [
      '/api/health',
      '/api/config',
      '/api/chat',
      '/api/models/openai',
      '/api/models/openai/refresh',
      '/api/models/openai/selected',
      '/api/models/openai/select',
      '/api/models/openai/default',
    ]) {
      expect(source).toContain(path)
    }
    expect(source).not.toContain('/api/market/prices')
    const setup = readFileSync(join(frontend, 'src/test/setup.ts'), 'utf8')
    expect(setup).toContain('./msw/handlers')
  })
})
