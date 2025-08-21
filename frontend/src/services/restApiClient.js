// REST API Client for the Stock Investment Assistant
class RestApiClient {
  constructor(baseUrl = 'http://localhost:5000') {
    this.baseUrl = baseUrl;
    this.defaultHeaders = { 'Content-Type': 'application/json' };
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = { headers: { ...this.defaultHeaders, ...options.headers }, ...options };
    const res = await fetch(url, config);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const ct = res.headers.get('content-type');
    return ct && ct.includes('application/json') ? res.json() : res.text();
  }

  async sendChat(message, { provider } = {}) {
    const body = { message, stream: false };
    if (provider) body.provider = provider;
    return this.request('/api/chat', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  /**
   * Stream chat response.
   * onChunk callback receives either:
   *  - string (content chunk)
   *  - object { event: 'meta', provider, model }
   *  - object { event: 'done', provider, model, fallback }
   */
  async streamChat(message, onChunk, { provider, signal } = {}) {
    const body = { message, stream: true };
    if (provider) body.provider = provider;

    const controller = new AbortController();
    if (signal) {
      // bridge external abort
      signal.addEventListener('abort', () => controller.abort(), { once: true });
    }

    const res = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: this.defaultHeaders,
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const reader = res.body?.getReader();
    if (!reader) throw new Error('Streaming not supported');

    const decoder = new TextDecoder();
    let full = '';
    let buffer = '';
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        let lineBreakIndex;
        while ((lineBreakIndex = buffer.indexOf('\n')) !== -1) {
          const rawLine = buffer.slice(0, lineBreakIndex);
          buffer = buffer.slice(lineBreakIndex + 1);
          const line = rawLine.trim();
          if (!line || !line.startsWith('data:')) continue;
          const data = line.slice(5).trim();
          if (!data) continue;
          if (data === '[DONE]') return full;
          let parsed;
          try {
            parsed = JSON.parse(data);
          } catch (e) {
            // Not JSON: might be plain text chunk
            continue;
          }
          if (parsed.event === 'meta') {
            onChunk?.(parsed); // structured meta event
            continue;
          }
          if (parsed.event === 'done') {
            onChunk?.(parsed); // final metadata
            continue; // don't append to full
          }
          if (parsed.error) {
            onChunk?.({ event: 'error', error: parsed.error });
            continue;
          }
          // Standard content chunk
          const piece = typeof parsed.chunk === 'string' ? parsed.chunk : '';
            if (piece) {
            full += piece;
            onChunk?.(piece);
          }
        }
      }
      // flush last buffer line (if any)
      const finalLine = buffer.trim();
      if (finalLine.startsWith('data:')) {
        const data = finalLine.slice(5).trim();
        if (data && data !== '[DONE]') {
          try {
            const parsed = JSON.parse(data);
            if (parsed.event === 'done') onChunk?.(parsed);
          } catch {
            // ignore
          }
        }
      }
      return full;
    } finally {
      try { reader.releaseLock(); } catch (_) { /* ignore */ }
    }
  }
}

export const restApiClient = new RestApiClient();
export default RestApiClient;
