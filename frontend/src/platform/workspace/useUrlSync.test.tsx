import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it } from 'vitest'
import { useSymbol, useWorkspaceStore } from './store'
import { useUrlSync } from './useUrlSync'

function Probe() {
  useUrlSync()
  return <main>ready</main>
}

describe('url sync', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('mirrors /sandbox/FPT and drops a direct write', async () => {
    render(
      <MemoryRouter initialEntries={['/sandbox/FPT']}>
        <Routes>
          <Route path="*" element={<Probe />} />
        </Routes>
      </MemoryRouter>,
    )
    expect(await screen.findByRole('main')).toBeTruthy()
    expect(useWorkspaceStore.getState().workspace.symbol).toBe('FPT')
    expect(useWorkspaceStore.getState().workspace.activeTrack).toBe('sandbox')
    useWorkspaceStore.setState((state) => ({
      workspace: { ...state.workspace, symbol: 'NOPE', coreObjectRef: { type: 'x', id: '1' } },
    }))
    expect(useWorkspaceStore.getState().workspace.symbol).toBe('FPT')
    expect(useWorkspaceStore.getState().workspace.coreObjectRef).toBeNull()
  })

  it('keeps theme dark and exports narrow selectors', () => {
    expect(useWorkspaceStore.getState().ui.theme).toBe('dark')
    expect(typeof useSymbol).toBe('function')
    const source = readFileSync(join(dirname(fileURLToPath(import.meta.url)), 'store.ts'), 'utf8')
    expect(source.includes('createContext')).toBe(false)
    expect(source.includes("'light'")).toBe(false)
  })
})
