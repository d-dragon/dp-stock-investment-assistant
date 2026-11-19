import { useLayoutEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { parsePathname, type TrackId } from './routeParams'
import { useWorkspaceStore } from './store'

export function useUrlSync(): void {
  const location = useLocation()
  const parsed = parsePathname(location.pathname)

  useLayoutEffect(() => {
    const apply = () => {
      if (parsed.notFound || !parsed.track) return
      useWorkspaceStore.getState().applyUrlMirrors({
        symbol: parsed.symbol,
        coreObjectRef: null,
        activeTrack: parsed.track,
      })
      useWorkspaceStore.getState().rememberRoute(parsed.track, location.pathname)
    }
    apply()
    return useWorkspaceStore.subscribe(() => {
      const workspace = useWorkspaceStore.getState().workspace
      if (parsed.notFound || !parsed.track) return
      const drifted =
        workspace.symbol !== parsed.symbol ||
        workspace.activeTrack !== parsed.track ||
        workspace.coreObjectRef !== null
      if (drifted) apply()
    })
  }, [location.pathname, parsed.notFound, parsed.symbol, parsed.track])
}

export function routeForTrack(track: TrackId): string {
  return useWorkspaceStore.getState().workspace.lastRouteByTrack[track] ?? `/${track}`
}
