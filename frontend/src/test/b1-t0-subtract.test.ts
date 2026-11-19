import { readdirSync, readFileSync, statSync } from 'node:fs'
import { dirname, join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const srcRoot = join(dirname(fileURLToPath(import.meta.url)), '..')

// Split so this test file is not itself a hit for the proving search under src.
const forbidden = ['Message' + 'Formatter', 'dangerouslySet' + 'InnerHTML', 'REACT_' + 'APP_']

function sourceFiles(dir: string): string[] {
  const found: string[] = []
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry)
    if (statSync(path).isDirectory()) {
      if (entry === 'test') {
        continue
      }
      found.push(...sourceFiles(path))
      continue
    }
    found.push(path)
  }
  return found
}

describe('B1 T0 subtract', () => {
  it('leaves no unsafe formatter, raw HTML render, or CRA env prefix under src', () => {
    const hits: string[] = []
    for (const file of sourceFiles(srcRoot)) {
      const text = readFileSync(file, 'utf8')
      if (forbidden.some((needle) => text.includes(needle))) {
        hits.push(relative(srcRoot, file))
      }
    }
    expect(hits).toEqual([])
  })
})
