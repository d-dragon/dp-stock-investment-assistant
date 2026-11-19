import { existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { ESLint } from 'eslint'
import { describe, expect, it } from 'vitest'

const frontend = join(dirname(fileURLToPath(import.meta.url)), '../..')

async function errors(file: string): Promise<number> {
  const eslint = new ESLint({ cwd: frontend })
  const results = await eslint.lintFiles([file])
  return results.reduce((sum, result) => sum + result.errorCount, 0)
}

describe('B3 lint backstops', () => {
  it('fails a feature colour, a jsx literal, and a legacy import', async () => {
    expect(await errors('eslint-fixtures/b3-feature-color.tsx')).toBeGreaterThan(0)
    expect(await errors('eslint-fixtures/b3-feature-stream.ts')).toBeGreaterThan(0)
    expect(await errors('eslint-fixtures/b3-jsx-literal.tsx')).toBeGreaterThan(0)
    expect(await errors('eslint-fixtures/b3-legacy-components-import.ts')).toBeGreaterThan(0)
  }, 30000)

  it('leaves the legacy stylesheets absent', () => {
    expect(existsSync(join(frontend, 'src/App.css'))).toBe(false)
    expect(existsSync(join(frontend, 'src/index.css'))).toBe(false)
  })
})
