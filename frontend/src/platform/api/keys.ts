export const qk = {
  health: () => ['health'] as const,
  config: () => ['config'] as const,
  models: (provider: string) => ['models', provider] as const,
}
