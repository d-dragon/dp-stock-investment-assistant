import { useParams } from 'react-router-dom'
import { parseSymbol, parseTrack } from '../platform/workspace/routeParams'
import { NotFoundFrame } from './router'

export function TrackView() {
  const { track } = useParams()
  const parsed = parseTrack(track)
  if (!parsed) return <NotFoundFrame />
  return parsed === 'sandbox' ? <div data-chart-slot="" /> : <div data-track-ready="" />
}

export function SymbolView() {
  const { track, symbol } = useParams()
  if (!parseTrack(track) || !parseSymbol(symbol)) return <NotFoundFrame />
  return parseTrack(track) === 'sandbox' ? <div data-chart-slot="" /> : <div data-track-ready="" />
}
