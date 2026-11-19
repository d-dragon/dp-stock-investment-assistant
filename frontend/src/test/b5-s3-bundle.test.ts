import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const frontend = join(dirname(fileURLToPath(import.meta.url)), '../..')

describe('production bundle', () => {
  it('loads the browser worker only behind VITE_USE_MOCKS', () => {
    const main = readFileSync(join(frontend, 'src/main.tsx'), 'utf8')
    expect(main).toContain("import.meta.env.VITE_USE_MOCKS === 'true'")
    expect(main).toContain("import('./mocks/browser')")
    const browser = readFileSync(join(frontend, 'src/mocks/browser.ts'), 'utf8')
    expect(browser).toContain("dataset.mocks = 'on'")
    const pkg = readFileSync(join(frontend, 'package.json'), 'utf8')
    expect(pkg).not.toMatch(/"build": "[^"]*VITE_USE_MOCKS/)
  })
})
