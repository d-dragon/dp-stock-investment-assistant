import { describe, expect, it } from 'vitest'
import config from '../../tailwind.config'

function collectKeys(value: unknown, found: string[] = []): string[] {
  if (!value || typeof value !== 'object') return found
  for (const [key, child] of Object.entries(value as Record<string, unknown>)) {
    found.push(key)
    collectKeys(child, found)
  }
  return found
}

describe('tailwind market and state utilities', () => {
  it('exposes no market or state colour utilities', () => {
    const keys = collectKeys(config)
    expect(keys).not.toContain('market')
    expect(keys).not.toContain('state')
  })
})
