import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import * as report from '../../platform/observability/reportError'
import { ZoneHost } from './ZoneHost'

function Boom(): null {
  throw new Error('zone blew up')
}

function Ok({ label }: { label: string }) {
  return <p>{label}</p>
}

describe('ZoneHost', () => {
  it('isolates a throw to one zone', () => {
    const spy = vi.spyOn(report, 'reportError').mockImplementation(() => undefined)
    render(
      <div>
        <ZoneHost zone="z1">
          <Ok label="z1-ok" />
        </ZoneHost>
        <ZoneHost zone="z3">
          <Boom />
        </ZoneHost>
        <ZoneHost zone="z2">
          <Ok label="z2-ok" />
        </ZoneHost>
        <ZoneHost zone="z4">
          <Ok label="z4-ok" />
        </ZoneHost>
      </div>,
    )
    expect(screen.getByText('z1-ok')).toBeTruthy()
    expect(screen.getByText('z2-ok')).toBeTruthy()
    expect(screen.getByText('z4-ok')).toBeTruthy()
    expect(document.querySelector('[data-zone="z3"]')?.getAttribute('data-state')).toBe('error')
    expect(spy).toHaveBeenCalledWith(expect.any(Error), expect.objectContaining({ zone: 'z3' }))
  })
})
