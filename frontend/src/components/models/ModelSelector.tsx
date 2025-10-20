import React, { useState, useEffect } from 'react';
import { modelsApi } from '../../services/modelsApi';
import { OpenAIModel, ModelListResponse, ModelSelection } from '../../types/models';

interface ModelSelectorProps {
  onModelChange?: (provider: string, modelName: string) => void;
  disabled?: boolean;
  compact?: boolean;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ 
  onModelChange, 
  disabled = false,
  compact = false 
}) => {
  const [models, setModels] = useState<OpenAIModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<ModelSelection | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cacheStatus, setCacheStatus] = useState<'cache' | 'openai'>('cache');

  // Load models and current selection on mount
  useEffect(() => {
    let isMounted = true;

    const loadModels = async (refresh: boolean = false) => {
      try {
        setIsLoading(true);
        setError(null);
        const response: ModelListResponse = await modelsApi.listModels(refresh);
        if (!isMounted) return;
        setModels(response.models);
        setCacheStatus(response.source);
      } catch (err: any) {
        if (!isMounted) return;
        setError(err.message || 'Failed to load models');
        console.error('Failed to load models:', err);
      } finally {
        if (!isMounted) return;
        setIsLoading(false);
      }
    };

    const loadSelectedModel = async () => {
      try {
        const selection = await modelsApi.getSelectedModel();
        if (!isMounted) return;
        setSelectedModel(selection);
      } catch (err: any) {
        if (!isMounted) return;
        console.error('Failed to load selected model:', err);
        // Non-critical error, don't show to user
      }
    };

    loadModels();
    loadSelectedModel();

    return () => {
      isMounted = false;
    };
  }, []);

  // loadModels and loadSelectedModel are now defined inside useEffect with isMounted guard.
  const handleRefresh = async () => {
    try {
      setIsRefreshing(true);
      setError(null);
      const response = await modelsApi.refreshModels();
      setModels(response.models);
      setCacheStatus(response.source);
    } catch (err: any) {
      setError(err.message || 'Failed to refresh models');
      console.error('Failed to refresh models:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleModelSelect = async (event: React.ChangeEvent<HTMLSelectElement>) => {
    const modelId = event.target.value;
    if (!modelId) return;

    try {
      setError(null);
      const response = await modelsApi.selectModel({
        provider: 'openai',
        name: modelId
      });
      setSelectedModel(response);
      
      // Notify parent component
      if (onModelChange) {
        onModelChange(response.provider, response.name);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to select model');
      console.error('Failed to select model:', err);
    }
  };

  // Compact view for header
  if (compact) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <select
          value={selectedModel?.name || ''}
          onChange={handleModelSelect}
          disabled={disabled || isLoading || models.length === 0}
          style={{
            padding: '4px 8px',
            fontSize: 14,
            border: '1px solid #ddd',
            borderRadius: 4,
            backgroundColor: 'white',
            cursor: disabled || isLoading ? 'not-allowed' : 'pointer'
          }}
          title="Select OpenAI model"
        >
          {isLoading ? (
            <option>Loading...</option>
          ) : models.length === 0 ? (
            <option>No models available</option>
          ) : (
            <>
              <option value="" disabled>Select model</option>
              {models.map(model => (
                <option key={model.id} value={model.id}>
                  {model.id}
                </option>
              ))}
            </>
          )}
        </select>
        <button
          onClick={handleRefresh}
          disabled={disabled || isRefreshing}
          style={{
            padding: '4px 8px',
            fontSize: 12,
            border: '1px solid #ddd',
            borderRadius: 4,
            backgroundColor: 'white',
            cursor: disabled || isRefreshing ? 'not-allowed' : 'pointer'
          }}
          title="Refresh model list from OpenAI"
          aria-label="Refresh model list"
          aria-busy={isRefreshing}
        >
          {isRefreshing ? '⟳' : '↻'}
        </button>
      </div>
    );
  }

  // Full view
  return (
    <div style={{ padding: 12, border: '1px solid #ddd', borderRadius: 6, backgroundColor: '#f9f9f9' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h3 style={{ margin: 0, fontSize: 16 }}>OpenAI Model Selection</h3>
        <button
          onClick={handleRefresh}
          disabled={disabled || isRefreshing}
          style={{
            padding: '6px 12px',
            fontSize: 14,
            border: '1px solid #2196f3',
            borderRadius: 4,
            backgroundColor: disabled || isRefreshing ? '#ccc' : '#2196f3',
            color: 'white',
            cursor: disabled || isRefreshing ? 'not-allowed' : 'pointer'
          }}
        >
          {isRefreshing ? 'Refreshing...' : 'Refresh List'}
        </button>
      </div>

      {error && (
        <div style={{
          padding: 8,
          marginBottom: 12,
          backgroundColor: '#ffebee',
          border: '1px solid #f44336',
          borderRadius: 4,
          color: '#c62828',
          fontSize: 14
        }}>
          {error}
        </div>
      )}

      <div style={{ marginBottom: 12 }}>
        <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 500 }}>
          Current Model:
        </label>
        <div style={{ fontSize: 14, color: '#666' }}>
          {selectedModel ? (
            <>
              <strong>{selectedModel.name}</strong> ({selectedModel.provider})
            </>
          ) : (
            'Loading...'
          )}
        </div>
      </div>

      <div>
        <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 500 }}>
          Available Models:
        </label>
        <select
          value={selectedModel?.name || ''}
          onChange={handleModelSelect}
          disabled={disabled || isLoading || models.length === 0}
          style={{
            width: '100%',
            padding: 8,
            fontSize: 14,
            border: '1px solid #ddd',
            borderRadius: 4,
            backgroundColor: 'white',
            cursor: disabled || isLoading ? 'not-allowed' : 'pointer'
          }}
        >
          {isLoading ? (
            <option>Loading models...</option>
          ) : models.length === 0 ? (
            <option>No models available</option>
          ) : (
            models.map(model => (
              <option key={model.id} value={model.id}>
                {model.id} (owned by: {model.owned_by})
              </option>
            ))
          )}
        </select>
      </div>

      <div style={{ marginTop: 12, fontSize: 12, color: '#666' }}>
        {models.length > 0 && (
          <>
            {models.length} models available · Source: {cacheStatus === 'cache' ? '💾 Cache' : '🌐 OpenAI API'}
          </>
        )}
      </div>
    </div>
  );
};

export default ModelSelector;
