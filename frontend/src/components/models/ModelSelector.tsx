import React, { useState, useEffect } from 'react';
import { StatusBadge } from '../../design-system/patterns/StatusBadge/StatusBadge';
import { modelsApi } from '../../platform/api/client';
import { t } from '../../platform/i18n/t';
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
        const response: ModelListResponse = refresh 
          ? await modelsApi.refreshModels() 
          : await modelsApi.listModels();
        if (!isMounted) return;
        setModels(response.models);
        setCacheStatus(response.source);
      } catch (err: any) {
        if (!isMounted) return;
        setError(err.message || t('models.loadFailed'));
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
      setError(err.message || t('models.refreshFailed'));
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
      setError(err.message || t('models.selectFailed'));
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
            border: '1px solid var(--surface-line)',
            borderRadius: 4,
            backgroundColor: 'var(--surface-card)',
            color: 'var(--surface-text)',
            cursor: disabled || isLoading ? 'not-allowed' : 'pointer'
          }}
          title={t('models.select')}
        >
          {isLoading ? (
            <option>{t('models.loading')}</option>
          ) : models.length === 0 ? (
            <option>{t('models.empty')}</option>
          ) : (
            <>
              <option value="" disabled>{t('models.select')}</option>
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
            border: '1px solid var(--surface-line)',
            borderRadius: 4,
            backgroundColor: 'var(--surface-card)',
            color: 'var(--surface-text)',
            cursor: disabled || isRefreshing ? 'not-allowed' : 'pointer'
          }}
          title={t('models.refresh')}
          aria-label={t('models.refresh')}
          aria-busy={isRefreshing}
        >
          {isRefreshing ? '⟳' : '↻'}
        </button>
      </div>
    );
  }

  // Full view
  return (
    <div style={{ padding: 12, border: '1px solid var(--surface-line)', borderRadius: 6, backgroundColor: 'var(--surface-card)', color: 'var(--surface-text)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h3 style={{ margin: 0, fontSize: 16 }}>{t('models.title')}</h3>
        <button
          onClick={handleRefresh}
          disabled={disabled || isRefreshing}
          style={{
            padding: '6px 12px',
            fontSize: 14,
            border: '1px solid var(--surface-line)',
            borderRadius: 4,
            backgroundColor: 'var(--surface-bg)',
            color: 'var(--surface-text)',
            cursor: disabled || isRefreshing ? 'not-allowed' : 'pointer'
          }}
        >
          {isRefreshing ? t('models.refreshing') : t('models.refreshList')}
        </button>
      </div>

      {error && (
        <div style={{ marginBottom: 12 }}>
          <StatusBadge status="danger" label={error} />
        </div>
      )}

      <div style={{ marginBottom: 12 }}>
        <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 500 }}>
          {t('models.current')}
        </label>
        <div style={{ fontSize: 14, color: 'var(--surface-text2)' }}>
          {selectedModel ? (
            <>
              <strong>{selectedModel.name}</strong> ({selectedModel.provider})
            </>
          ) : (
            t('models.loading')
          )}
        </div>
      </div>

      <div>
        <label style={{ display: 'block', marginBottom: 4, fontSize: 14, fontWeight: 500 }}>
          {t('models.available')}
        </label>
        <select
          value={selectedModel?.name || ''}
          onChange={handleModelSelect}
          disabled={disabled || isLoading || models.length === 0}
          style={{
            width: '100%',
            padding: 8,
            fontSize: 14,
            border: '1px solid var(--surface-line)',
            borderRadius: 4,
            backgroundColor: 'var(--surface-bg)',
            color: 'var(--surface-text)',
            cursor: disabled || isLoading ? 'not-allowed' : 'pointer'
          }}
        >
          {isLoading ? (
            <option>{t('models.loadingList')}</option>
          ) : models.length === 0 ? (
            <option>{t('models.empty')}</option>
          ) : (
            models.map(model => (
              <option key={model.id} value={model.id}>
                {model.id} ({t('models.ownedBy')}: {model.owned_by})
              </option>
            ))
          )}
        </select>
      </div>

      <div style={{ marginTop: 12, fontSize: 12, color: 'var(--surface-text2)' }}>
        {models.length > 0 && (
          <>
            {models.length} {t('models.availableSuffix')} · {cacheStatus === 'cache' ? t('models.sourceCache') : t('models.sourceLive')}
          </>
        )}
      </div>
    </div>
  );
};

export default ModelSelector;
