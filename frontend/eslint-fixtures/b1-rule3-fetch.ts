// fetch is allowed only inside platform/api and platform/stream (rule 3).
export async function loadOutsidePlatform(): Promise<Response> {
  return fetch('/api/health')
}
