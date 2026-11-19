import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { modelsApi } from '../../platform/api/client'
import { qk } from '../../platform/api/keys'
import { t } from '../../platform/i18n/t'
import type { ModelSelection } from '../../types/models'

export interface ModelSelectorProps {
  onModelChange?: (provider: string, modelName: string) => void
  disabled?: boolean
  compact?: boolean
}

export function ModelSelector({ onModelChange, disabled = false, compact = false }: ModelSelectorProps) {
  const client = useQueryClient()
  const models = useQuery({
    queryKey: qk.models('openai'),
    queryFn: async () => {
      const [list, current] = await Promise.all([modelsApi.listModels(), modelsApi.getSelectedModel()])
      return { list, current }
    },
  })
  const select = useMutation({
    mutationFn: (name: string) => modelsApi.selectModel({ provider: 'openai', name }),
    onSuccess: (next: ModelSelection) => {
      client.setQueryData(
        qk.models('openai'),
        (prev: { list: { models: { id: string }[] }; current: ModelSelection } | undefined) =>
          prev ? { ...prev, current: next } : prev,
      )
      onModelChange?.(next.provider, next.name)
    },
  })

  const options = models.data?.list.models ?? []
  const selectedName = models.data?.current.name ?? ''

  return (
    <select
      aria-label={t('models.select')}
      title={compact ? t('models.select') : undefined}
      value={selectedName}
      disabled={disabled || models.isPending || select.isPending}
      onChange={(event) => {
        if (event.target.value) select.mutate(event.target.value)
      }}
    >
      <option value="">{models.isPending ? t('models.loading') : t('models.empty')}</option>
      {options.map((model) => (
        <option key={model.id} value={model.id}>
          {model.id}
        </option>
      ))}
    </select>
  )
}
