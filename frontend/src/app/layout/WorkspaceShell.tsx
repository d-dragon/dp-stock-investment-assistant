import { useEffect, useState, type ReactNode } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { Link, Outlet } from 'react-router-dom'
import { Companion } from '../../features/companion'
import { ModelSelector } from '../../features/models'
import { fmt } from '../../platform/format/format'
import { t } from '../../platform/i18n/t'
import { showsAccessNotFound, type TrackId } from '../../platform/workspace/routeParams'
import {
  useActiveTrack,
  useLastRouteByTrack,
  usePaneSizes,
  useSymbol,
  useUrlSync,
  useWorkspaceStore,
  useZ4Collapsed,
} from '../../platform/workspace'
import type { SessionRef } from '../../platform/api/sessionRef'
import { getUUID } from '../../utils/uuid'
import { ZoneHost } from './ZoneHost'
import styles from './shell.module.css'

function shellSession(): SessionRef {
  const key = 'dp-stock:session-ref'
  const saved = sessionStorage.getItem(key)
  if (saved) return JSON.parse(saved) as SessionRef
  const next = { sessionId: getUUID(), conversationId: getUUID() }
  sessionStorage.setItem(key, JSON.stringify(next))
  return next
}

function useViewportWidth(): number {
  const [width, setWidth] = useState(() => window.innerWidth)
  useEffect(() => {
    const onResize = () => setWidth(window.innerWidth)
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])
  return width
}

function TrackIcon({ track }: { track: TrackId }) {
  return (
    <svg data-track-icon="" viewBox="0 0 16 16" className={styles.trackIcon} aria-hidden="true">
      {track === 'sandbox' ? (
        <path fill="currentColor" d="M2 12h3V8H2v4zm4.5 0H10V4H6.5v8zM11 12h3V6h-3v6z" />
      ) : (
        <path fill="currentColor" d="M2 3.5h12v2H2v-2zm0 3.5h12v2H2V7zm0 3.5h8v2H2v-2z" />
      )}
    </svg>
  )
}

function TrackLink({ track, rail }: { track: TrackId; rail: boolean }) {
  const active = useActiveTrack()
  const last = useLastRouteByTrack()
  const label = track === 'sandbox' ? t('shell.track.sandbox') : t('shell.track.portfolio')
  return (
    <Link
      to={last[track] ?? `/${track}`}
      aria-label={label}
      title={label}
      aria-current={active === track ? 'page' : undefined}
      className={active === track ? styles.activeMark : undefined}
    >
      {rail ? <TrackIcon track={track} /> : null}
      <span className={rail ? styles.railLabel : undefined}>{label}</span>
    </Link>
  )
}

function Zone({
  zone,
  role,
  label,
  children,
  frameStyle,
}: {
  zone: 'z1' | 'z2' | 'z3' | 'z4'
  role: 'banner' | 'navigation' | 'main' | 'complementary'
  label: string
  children?: ReactNode
  frameStyle?: { width: number }
}) {
  const Tag = role === 'banner' ? 'header' : role === 'navigation' ? 'nav' : role === 'main' ? 'main' : 'aside'
  return (
    <ZoneHost zone={zone}>
      <Tag id={`zone-${zone}`} role={role} tabIndex={0} data-zone={zone} aria-label={label} style={frameStyle}>
        {children}
      </Tag>
    </ZoneHost>
  )
}

export function WorkspaceShell({ accessStatus }: { accessStatus?: number }) {
  useUrlSync()
  const [sessionRef] = useState(shellSession)
  const width = useViewportWidth()
  const symbol = useSymbol()
  const track = useActiveTrack()
  const paneSizes = usePaneSizes()
  const sizes = paneSizes[track]
  const z4Collapsed = useZ4Collapsed()
  const docked = width >= 1440
  const rail = width < 1024
  const drawerOpen = !z4Collapsed
  const denied = accessStatus !== undefined && showsAccessNotFound(accessStatus)

  const z1 = (
    <Zone zone="z1" role="navigation" label={t('shell.zone.z1')} frameStyle={rail ? { width: 56 } : undefined}>
      <div className={rail ? styles.rail : undefined}>
        <TrackLink track="sandbox" rail={rail} />
        <TrackLink track="portfolio" rail={rail} />
        <div role="group" aria-label={t('shell.z1.lifecycle')} data-lifecycle="" />
      </div>
    </Zone>
  )

  const z3 = (
    <Zone zone="z3" role="main" label={t('shell.zone.z3')}>
      {denied ? <p role="status">{t('shell.notFound')}</p> : <Outlet />}
      {!symbol && !denied ? <p>{t('shell.z3.emptyInvitation')}</p> : null}
    </Zone>
  )

  const z4 = (
    <Zone zone="z4" role="complementary" label={t('shell.zone.z4')}>
      <ModelSelector compact />
      <Companion sessionRef={sessionRef} />
    </Zone>
  )

  return (
    <div className={styles.focus} data-ui="shell">
      <h1>{t('app.title')}</h1>
      <span data-fmt aria-hidden="true">
        {fmt.volume(null)}
      </span>
      <a href="#zone-z3">{t('shell.skipToWorkspace')}</a>
      <Zone zone="z2" role="banner" label={t('shell.zone.z2')}>
        {!symbol ? <p>{t('shell.z2.emptySymbol')}</p> : <p>{symbol}</p>}
        {docked ? null : (
          <button
            type="button"
            aria-expanded={drawerOpen}
            aria-controls="zone-z4"
            onClick={() => useWorkspaceStore.getState().setCollapsed('z4', drawerOpen)}
          >
            {t('shell.z4.toggle')}
          </button>
        )}
      </Zone>
      {docked ? (
        <PanelGroup
          direction="horizontal"
          onLayout={(next) => {
            if (next.length !== 3) return
            useWorkspaceStore.getState().setPaneSizes(track, [next[0], next[1], next[2]])
          }}
        >
          <Panel id="z1" defaultSize={sizes[0]} minSize={12}>
            {z1}
          </Panel>
          <PanelResizeHandle />
          <Panel id="z3" defaultSize={sizes[1]} minSize={30}>
            {z3}
          </Panel>
          <PanelResizeHandle />
          <Panel id="z4" defaultSize={sizes[2]} minSize={12}>
            {z4}
          </Panel>
        </PanelGroup>
      ) : (
        <div className={styles.row}>
          <div className={rail ? styles.railCol : styles.dockCol}>{z1}</div>
          <div className={styles.mainCol}>{z3}</div>
          {drawerOpen ? <div className={styles.drawer}>{z4}</div> : null}
        </div>
      )}
    </div>
  )
}
