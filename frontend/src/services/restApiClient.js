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

  async sendChat(message) {
    return this.request('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, stream: false }),
    });
  }

  async streamChat(message, onChunk) {
    const res = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: this.defaultHeaders,
      body: JSON.stringify({ message, stream: true }),
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const reader = res.body?.getReader();
    if (!reader) throw new Error('Streaming not supported');

    const decoder = new TextDecoder();
    let full = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunkStr = decoder.decode(value);
      for (const line of chunkStr.split('\n')) {
        const t = line.trim();
        if (!t || !t.startsWith('data:')) continue;
        const data = t.slice(5).trim();
        if (data === '[DONE]') return full;
        try {
          const parsed = JSON.parse(data);
          const piece = parsed?.chunk ?? '';
          if (piece) {
            full += piece;
            onChunk?.(piece);
          }
        } catch {
          // ignore malformed lines
        }
      }
    }
    return full;
  }
}

export const restApiClient = new RestApiClient();
export default RestApiClient;
