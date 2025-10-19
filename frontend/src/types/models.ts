// Model-related type definitions

export interface OpenAIModel {
  id: string;
  created: number;
  owned_by: string;
  object: string;
}

export interface ModelListResponse {
  models: OpenAIModel[];
  fetched_at: string;
  source: 'cache' | 'openai';
  cached: boolean;
}

export interface ModelSelection {
  provider: string;
  name: string;
}

export interface SelectModelRequest {
  provider?: string;
  name: string;
}

export interface SetDefaultModelRequest {
  model: string;
}

export interface SetDefaultModelResponse {
  model: string;
  provider: string;
  active_model: string;
}
