// Models API Service - OpenAI model management endpoints

import { 
  ModelListResponse, 
  ModelSelection, 
  SelectModelRequest,
  SetDefaultModelRequest,
  SetDefaultModelResponse
} from '../types/models';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class ModelsApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * List available OpenAI models (cached by default)
   */
  async listModels(): Promise<ModelListResponse> {
    const url = `${this.baseUrl}/api/models/openai`;
    const response = await fetch(url);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Failed to list models' }));
      throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * Force refresh the OpenAI models cache
   */
  async refreshModels(): Promise<ModelListResponse> {
    const url = `${this.baseUrl}/api/models/openai/refresh`;
    const response = await fetch(url, { method: 'POST' });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Failed to refresh models' }));
      throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * Get the currently selected model
   */
  async getSelectedModel(): Promise<ModelSelection> {
    const url = `${this.baseUrl}/api/models/openai/selected`;
    const response = await fetch(url);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Failed to get selected model' }));
      throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * Select a model to use for chat
   * @param request - Provider and model name
   */
  async selectModel(request: SelectModelRequest): Promise<ModelSelection> {
    const url = `${this.baseUrl}/api/models/openai/select`;
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Failed to select model' }));
      throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * Set the default OpenAI model (legacy endpoint)
   * @param modelName - The model name to set as default
   */
  async setDefaultModel(modelName: string): Promise<SetDefaultModelResponse> {
    const url = `${this.baseUrl}/api/models/openai/default`;
    const request: SetDefaultModelRequest = { model: modelName };
    
    const response = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Failed to set default model' }));
      throw new Error(error.error || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
}

export const modelsApi = new ModelsApiService();
export default ModelsApiService;
