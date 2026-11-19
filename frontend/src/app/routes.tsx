import { lazy, Suspense, type ReactNode } from 'react'
import { createBrowserRouter, createMemoryRouter, type RouteObject } from 'react-router-dom'
import { WorkspaceShell } from './layout/WorkspaceShell'
import { IndexRedirect, NotFoundFrame } from './router'

const TrackRoute = lazy(() => import('./route-views').then((mod) => ({ default: mod.TrackView })))
const SymbolRoute = lazy(() => import('./route-views').then((mod) => ({ default: mod.SymbolView })))

function LazyRoute({ children }: { children: ReactNode }) {
  return <Suspense fallback={null}>{children}</Suspense>
}

export function shellRoutes(accessStatus?: number): RouteObject[] {
  return [
    {
      path: '/',
      element: <WorkspaceShell accessStatus={accessStatus} />,
      children: [
        { index: true, element: <IndexRedirect /> },
        { path: ':track', element: <LazyRoute><TrackRoute /></LazyRoute> },
        { path: ':track/:symbol', element: <LazyRoute><SymbolRoute /></LazyRoute> },
        { path: '*', element: <NotFoundFrame /> },
      ],
    },
  ]
}

export function createAppRouter() {
  return createBrowserRouter(shellRoutes())
}

export function createTestRouter(path: string, accessStatus?: number) {
  return createMemoryRouter(shellRoutes(accessStatus), { initialEntries: [path] })
}
