import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const root = join(dirname(fileURLToPath(import.meta.url)), '../../..')

describe('frontend CI order', () => {
  it('keeps the delivery 1 steps and then runs Storybook and Playwright', () => {
    const ci = readFileSync(join(root, '.github/workflows/frontend-ci.yml'), 'utf8')
    const lint = ci.indexOf('npm run lint')
    const tsc = ci.indexOf('tsc --noEmit')
    const vitest = ci.indexOf('vitest run')
    const build = ci.indexOf('npm run build')
    const drift = ci.indexOf('gen:api')
    const story = ci.indexOf('build-storybook')
    const storyAxe = ci.indexOf('vitest run --project storybook')
    const e2e = ci.indexOf('playwright test')
    expect(lint).toBeGreaterThan(0)
    expect(tsc).toBeGreaterThan(lint)
    expect(vitest).toBeGreaterThan(tsc)
    expect(build).toBeGreaterThan(vitest)
    expect(drift).toBeGreaterThan(build)
    expect(story).toBeGreaterThan(drift)
    expect(storyAxe).toBeGreaterThan(story)
    expect(e2e).toBeGreaterThan(storyAxe)
    const docker = readFileSync(join(root, '.github/workflows/build-push-dockerhub.yml'), 'utf8')
    expect(docker).toContain('branches: [ main ]')
    expect(docker).toContain('workflow_dispatch')
  })
})
