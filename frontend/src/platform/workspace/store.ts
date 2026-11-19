import { create } from 'zustand'
import type { TrackId } from './routeParams'

export interface CoreObjectRef {
  type: string
  id: string
}

export interface SymbolContext {
  lastCoreObjectRef: CoreObjectRef | null
  chart: { range: string; interval: string; seriesType: 'candle' | 'line' }
  z4ScrollTop: number
}

export interface WorkspaceSlice {
  symbol: string | null
  coreObjectRef: CoreObjectRef | null
  activeTrack: TrackId
  lastRouteByTrack: Record<TrackId, string | null>
}

export interface LayoutSlice {
  paneSizes: Record<TrackId, [number, number, number]>
  collapsed: { z1: boolean; z4: boolean }
}

export interface WorkspaceState {
  workspace: WorkspaceSlice
  context: { bySymbol: Record<string, SymbolContext> }
  layout: LayoutSlice
  ui: { theme: 'dark'; density: 'compact' }
  applyUrlMirrors: (next: {
    symbol: string | null
    coreObjectRef: CoreObjectRef | null
    activeTrack: TrackId
  }) => void
  rememberRoute: (track: TrackId, path: string) => void
  setPaneSizes: (track: TrackId, paneSizes: [number, number, number]) => void
  setCollapsed: (zone: 'z1' | 'z4', collapsed: boolean) => void
}

const emptySizes: [number, number, number] = [20, 55, 25]

function loadJson<T>(key: string, fallback: T): T {
  try {
    const raw = sessionStorage.getItem(key)
    if (!raw) return fallback
    return JSON.parse(raw) as T
  } catch {
    return fallback
  }
}

export const useWorkspaceStore = create<WorkspaceState>((set, get) => ({
  workspace: {
    symbol: null,
    coreObjectRef: null,
    activeTrack: 'sandbox',
    lastRouteByTrack: { sandbox: '/sandbox', portfolio: '/portfolio' },
  },
  context: loadJson('dp-stock:context', { bySymbol: {} }),
  layout: loadJson('dp-stock:layout', {
    paneSizes: { sandbox: emptySizes, portfolio: emptySizes },
    collapsed: { z1: false, z4: true },
  }),
  ui: { theme: 'dark', density: 'compact' },
  applyUrlMirrors: (next) => {
    const current = get().workspace
    if (
      current.symbol === next.symbol &&
      current.activeTrack === next.activeTrack &&
      current.coreObjectRef === next.coreObjectRef
    ) {
      return
    }
    set({ workspace: { ...current, ...next } })
  },
  rememberRoute: (track, path) => {
    const current = get().workspace
    if (current.lastRouteByTrack[track] === path) return
    set({
      workspace: {
        ...current,
        lastRouteByTrack: { ...current.lastRouteByTrack, [track]: path },
      },
    })
  },
  setPaneSizes: (track, paneSizes) => {
    const layout = get().layout
    const current = layout.paneSizes[track]
    if (current[0] === paneSizes[0] && current[1] === paneSizes[1] && current[2] === paneSizes[2]) return
    set({
      layout: {
        ...layout,
        paneSizes: { ...layout.paneSizes, [track]: paneSizes },
      },
    })
  },
  setCollapsed: (zone, collapsed) => {
    const layout = get().layout
    if (layout.collapsed[zone] === collapsed) return
    set({
      layout: {
        ...layout,
        collapsed: { ...layout.collapsed, [zone]: collapsed },
      },
    })
  },
}))

useWorkspaceStore.subscribe((state) => {
  sessionStorage.setItem('dp-stock:context', JSON.stringify(state.context))
  sessionStorage.setItem('dp-stock:layout', JSON.stringify(state.layout))
})

export const useSymbol = () => useWorkspaceStore((state) => state.workspace.symbol)
export const useActiveTrack = () => useWorkspaceStore((state) => state.workspace.activeTrack)
export const useCoreObjectRef = () => useWorkspaceStore((state) => state.workspace.coreObjectRef)
export const useLastRouteByTrack = () => useWorkspaceStore((state) => state.workspace.lastRouteByTrack)
export const usePaneSizes = () => useWorkspaceStore((state) => state.layout.paneSizes)
export const useZ4Collapsed = () => useWorkspaceStore((state) => state.layout.collapsed.z4)
export const useTheme = () => useWorkspaceStore((state) => state.ui.theme)
