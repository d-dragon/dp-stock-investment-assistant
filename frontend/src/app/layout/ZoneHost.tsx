import { Component, type ErrorInfo, type ReactNode } from 'react'
import { ZoneFrame } from '../../design-system/patterns/ZoneFrame'
import { reportError } from '../../platform/observability/reportError'

interface ZoneHostProps {
  zone: 'z1' | 'z2' | 'z3' | 'z4'
  children: ReactNode
}

interface ZoneHostState {
  failed: boolean
}

export class ZoneHost extends Component<ZoneHostProps, ZoneHostState> {
  state: ZoneHostState = { failed: false }

  static getDerivedStateFromError(): ZoneHostState {
    return { failed: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    reportError(error, { zone: this.props.zone, route: info.componentStack ?? undefined })
  }

  render() {
    if (this.state.failed) {
      return (
        <ZoneFrame
          zone={this.props.zone}
          state="error"
          onRetry={() => this.setState({ failed: false })}
        />
      )
    }
    return this.props.children
  }
}
