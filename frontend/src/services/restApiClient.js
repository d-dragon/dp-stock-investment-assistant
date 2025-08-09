// REST API Client for the Stock Investment Assistant
class RestApiClient {
  constructor(baseUrl = 'http://localhost:5000') {
    this.baseUrl = baseUrl;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        return await response.text();
      }
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Health check
  async checkHealth() {
    try {
      const response = await this.request('/api/health');
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Send chat message (with optional streaming)
  async sendChatMessage(message, streaming = false) {
    try {
      const response = await this.request('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message, stream: streaming }),
      });
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Get available commands
  async getCommands() {
    try {
      const response = await this.request('/api/commands');
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Get configuration
  async getConfig() {
    try {
      const response = await this.request('/api/config');
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Send message with streaming support
  async sendMessageWithStreaming(message, onChunk) {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat`, {
        method: 'POST',
        headers: this.defaultHeaders,
        body: JSON.stringify({ message, stream: true }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              return { success: true, data: { response: fullResponse } };
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.chunk) {
                fullResponse += parsed.chunk;
                if (onChunk) onChunk(parsed.chunk);
              }
            } catch (e) {
              // Ignore parsing errors for malformed chunks
            }
          }
        }
      }

      return { success: true, data: { response: fullResponse } };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Stock-specific endpoints
  async getStockPrice(symbol) {
    try {
      const response = await this.request(`/api/stock/${symbol}/price`);
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getStockAnalysis(symbol) {
    try {
      const response = await this.request(`/api/stock/${symbol}/analysis`);
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getMarketNews() {
    try {
      const response = await this.request('/api/market/news');
      return { success: true, data: response };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}

// Create and export a singleton instance
export const restApiClient = new RestApiClient();
export default RestApiClient;
