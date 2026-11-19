import type {
  ModelListResponse,
  ModelSelection,
  SelectModelRequest,
  SetDefaultModelResponse,
} from '../../types/models'
import { NoAuthAdapter } from '../auth/NoAuthAdapter'
import type { AuthAdapter } from '../auth/types'
import { ApiError, isRetriableStatus, safeMessage } from './errors'
import type { ChatRequestFields } from './sessionRef'

const ALLOWED_PATHS = [
  /^\/api\/health$/,
  /^\/api\/config$/,
  /^\/api\/models(?:\/|$)/,
  /^\/api\/chat$/,
]

const MUTATING = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

export interface ApiClientOptions {
  auth?: AuthAdapter
  fetchImpl?: typeof fetch
  baseUrl?: string
}

export interface ApiClient {
  apiFetch(path: string, init?: RequestInit): Promise<Response>
  request(method: string, path: string, body?: unknown): Promise<unknown>
  getHealth(): Promise<unknown>
  getConfig(): Promise<unknown>
  listModels(): Promise<ModelListResponse>
  refreshModels(): Promise<ModelListResponse>
  getSelectedModel(): Promise<ModelSelection>
  selectModel(body: SelectModelRequest): Promise<ModelSelection>
  setDefaultModel(modelName: string): Promise<SetDefaultModelResponse>
  postChat(body: ChatRequestFields): Promise<unknown>
}

function assertAllowed(path: string): void {
  const pathname = path.split('?')[0] ?? path
  if (!ALLOWED_PATHS.some((pattern) => pattern.test(pathname))) {
    throw new Error(`Path is not allowed for this client: ${pathname}`)
  }
}

async function toApiError(response: Response): Promise<ApiError> {
  const fallback = `http_${response.status}`
  let code = fallback
  let message = fallback
  const text = await response.text()
  if (text) {
    try {
      const parsed = JSON.parse(text) as { code?: unknown; message?: unknown }
      if (typeof parsed.code === 'string' && parsed.code.trim()) code = parsed.code
      message = safeMessage(parsed.message, fallback)
    } catch {
      message = safeMessage(text, fallback)
    }
  }
  return new ApiError(response.status, code, message, isRetriableStatus(response.status))
}

export function createApiClient(options: ApiClientOptions = {}): ApiClient {
  const auth = options.auth ?? new NoAuthAdapter()
  const fetchImpl = options.fetchImpl ?? fetch
  const base = (options.baseUrl ?? import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

  async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
    assertAllowed(path)
    const method = (init.method ?? 'GET').toUpperCase()
    const headers = new Headers(init.headers)
    headers.delete('Authorization')
    headers.delete('X-User-ID')
    if (MUTATING.has(method)) {
      for (const [name, value] of Object.entries(auth.csrfHeaders())) {
        headers.set(name, value)
      }
    }
    let response: Response
    try {
      response = await fetchImpl(`${base}${path}`, {
        ...init,
        method,
        headers,
        credentials: 'same-origin',
      })
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') throw err
      if (err instanceof Error && err.name === 'AbortError') throw err
      const message = err instanceof Error ? err.message : 'network'
      throw new ApiError(0, 'network', safeMessage(message, 'network'), true)
    }
    if (!response.ok) {
      if (response.status === 401) {
        await auth.onUnauthorized({ returnTo: window.location.pathname })
      }
      throw await toApiError(response)
    }
    return response
  }

  async function request(method: string, path: string, body?: unknown): Promise<unknown> {
    const response = await apiFetch(path, {
      method,
      headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
    const text = await response.text()
    if (!text) return null
    const contentType = response.headers.get('content-type') ?? ''
    if (contentType.includes('json')) return JSON.parse(text) as unknown
    return text
  }

  return {
    apiFetch,
    request,
    getHealth: () => request('GET', '/api/health'),
    getConfig: () => request('GET', '/api/config'),
    listModels: () => request('GET', '/api/models/openai') as Promise<ModelListResponse>,
    refreshModels: () => request('POST', '/api/models/openai/refresh') as Promise<ModelListResponse>,
    getSelectedModel: () => request('GET', '/api/models/openai/selected') as Promise<ModelSelection>,
    selectModel: (body) => request('POST', '/api/models/openai/select', body) as Promise<ModelSelection>,
    setDefaultModel: (modelName) =>
      request('PUT', '/api/models/openai/default', { model: modelName }) as Promise<SetDefaultModelResponse>,
    postChat: (body) => request('POST', '/api/chat', body),
  }
}

let singleton: ApiClient | undefined

export function getApiClient(): ApiClient {
  if (!singleton) singleton = createApiClient()
  return singleton
}

export function getHealth(): Promise<unknown> {
  return getApiClient().getHealth()
}

export function getConfig(): Promise<unknown> {
  return getApiClient().getConfig()
}

export const modelsApi = {
  listModels: () => getApiClient().listModels(),
  refreshModels: () => getApiClient().refreshModels(),
  getSelectedModel: () => getApiClient().getSelectedModel(),
  selectModel: (body: SelectModelRequest) => getApiClient().selectModel(body),
  setDefaultModel: (modelName: string) => getApiClient().setDefaultModel(modelName),
}
