import { http, HttpResponse } from 'msw'
import type { components } from '../platform/api/generated/schema'
import { chatSseFrames } from '../test/msw/chat-frames'

type Health = components['schemas']['HealthResponse']
type Config = components['schemas']['ConfigResponse']
type ModelList = components['schemas']['OpenAIModelListResponse']
type ModelSelection = components['schemas']['ModelSelectionResponse']
type SetDefault = components['schemas']['SetDefaultModelResponse']
type SelectBody = components['schemas']['SelectModelRequest']
type DefaultBody = components['schemas']['SetDefaultModelRequest']

const health: Health = { status: 'healthy', message: 'ok' }
const config: Config = {
  model: { provider: 'openai', name: 'gpt' },
  features: { yahoo_finance: false, alpha_vantage: false },
}

const modelList: ModelList = {
  models: [{ id: 'gpt', created: 0, owned_by: 'openai', object: 'model' }],
  fetched_at: '2026-11-19T00:00:00.000Z',
  source: 'cache',
  cached: true,
}

const selectedModel: ModelSelection = { provider: 'openai', name: 'gpt' }

export const handlers = [
  http.get('/api/health', () => HttpResponse.json(health)),
  http.get('/api/config', () => HttpResponse.json(config)),
  http.get('/api/models/openai', () => HttpResponse.json(modelList)),
  http.post('/api/models/openai/refresh', () => HttpResponse.json(modelList)),
  http.get('/api/models/openai/selected', () => HttpResponse.json(selectedModel)),
  http.post('/api/models/openai/select', async ({ request }) => {
    const body = (await request.json()) as SelectBody
    const next: ModelSelection = { provider: body.provider, name: body.name }
    return HttpResponse.json(next)
  }),
  http.put('/api/models/openai/default', async ({ request }) => {
    const body = (await request.json()) as DefaultBody
    const next: SetDefault = { model: body.model, provider: 'openai', active_model: body.model }
    return HttpResponse.json(next)
  }),
  http.post('/api/chat', () => {
    return new HttpResponse(chatSseFrames, {
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' },
    })
  }),
]
