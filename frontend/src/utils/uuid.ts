export function getUUID(): string {
  // Use Web Crypto when available, fall back to a safe random id
  try {
    // modern browsers / Node 18+: crypto.randomUUID()
    // @ts-ignore
    if (typeof crypto !== 'undefined' && typeof (crypto as any).randomUUID === 'function') {
      // @ts-ignore
      return (crypto as any).randomUUID();
    }
  } catch (e) {
    // ignore and fallback
  }
  // Fallback: reasonably unique id (not cryptographically strong)
  return 'id-' + Math.random().toString(36).slice(2) + '-' + Date.now().toString(36);
}