import { readdirSync, readFileSync, statSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const src = join(dirname(fileURLToPath(import.meta.url)), '..')
const frontend = join(src, '..')

function storyFiles(dir: string): string[] {
  const found: string[] = []
  for (const entry of readdirSync(dir)) {
    const path = join(dir, entry)
    if (statSync(path).isDirectory()) found.push(...storyFiles(path))
    else if (entry.endsWith('.stories.tsx')) found.push(path)
  }
  return found
}

function exportsOf(file: string): string[] {
  return [...readFileSync(file, 'utf8').matchAll(/export const (\w+)/g)].map((match) => match[1] ?? '')
}

describe('Storybook bound', () => {
  it('keeps a dark compact set of 11 to 15 stories', () => {
    const files = storyFiles(src)
    const stories = files.flatMap(exportsOf)
    expect(stories.length).toBeGreaterThanOrEqual(11)
    expect(stories.length).toBeLessThanOrEqual(15)
    const zone = exportsOf(files.find((file) => file.includes('ZoneFrame.stories.tsx')) ?? '')
    expect(zone).toEqual(['Empty', 'Loading', 'Ready', 'Stale', 'Error', 'Interrupted', 'Streaming'])
    for (const name of ['PriceCell.stories.tsx', 'Delta.stories.tsx', 'StatusBadge.stories.tsx', 'MessageBody.stories.tsx']) {
      expect(files.some((file) => file.endsWith(name))).toBe(true)
    }
    const preview = readFileSync(join(frontend, '.storybook/preview.tsx'), 'utf8')
    expect(preview).toContain('data-theme')
    expect(preview).toContain('dark')
    expect(preview).toContain('data-density')
    expect(preview).toContain('compact')
    expect(preview).not.toContain('theme-toggle')
    expect(preview).toContain('afterEach')
    expect(preview).toContain('axe.run')
    expect(preview).not.toContain('beforeEach')
  })
})
