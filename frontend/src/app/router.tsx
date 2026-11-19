import { Navigate } from 'react-router-dom'
import { t } from '../platform/i18n/t'

export function NotFoundFrame() {
  return <p role="status">{t('shell.notFound')}</p>
}

export function IndexRedirect() {
  return <Navigate to="/sandbox" replace />
}
