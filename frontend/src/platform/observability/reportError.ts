export interface ReportContext {
  zone: 'z1' | 'z2' | 'z3' | 'z4'
  route?: string
}

export function reportError(error: unknown, context: ReportContext): void {
  console.error(context.zone, error)
}
