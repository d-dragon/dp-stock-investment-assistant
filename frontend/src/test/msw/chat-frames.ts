/** Frames from docs/domains/frontend/TECHNICAL_DESIGN.md — "6.2 Today's stream contract". */
export const chatSseFrames = [
  'data: {"event":"meta","provider":"openai","model":"gpt-4"}',
  'data: {"chunk":"AAPL "}',
  'data: {"event":"done","fallback":false,"provider":"openai","model":"gpt-4"}',
  'data: [DONE]',
  '',
].join('\n')
