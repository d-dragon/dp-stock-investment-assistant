export interface StatusBadgeProps {
  status: 'info' | 'success' | 'warn' | 'danger' | 'streaming'
  label: string
}

const stateColour: Record<StatusBadgeProps['status'], string> = {
  info: 'var(--state-info)',
  success: 'var(--state-success)',
  warn: 'var(--state-warn)',
  danger: 'var(--state-danger)',
  streaming: 'var(--state-streaming)',
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  return (
    <span role="status" data-state={status} style={{ color: stateColour[status] }}>
      <svg aria-hidden="true" viewBox="0 0 8 8" width="8" height="8">
        <circle cx="4" cy="4" r="3" fill="currentColor" />
      </svg>
      {label}
    </span>
  )
}
