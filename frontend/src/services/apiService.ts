import { API_CONFIG } from '../config';

export interface Message {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface Command {
  command: string;
  description: string;
  example?: string;
}

export interface ChatResponse {
  response: string;
  timestamp: string;
}

export interface ApiError {
  error: string;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL;
  }

  async healthCheck(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.HEALTH}`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  }

  async sendMessage(message: string): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.CHAT}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.error || 'Failed to send message');
    }

    return response.json();
  }

  async sendMessageStreaming(message: string, onChunk: (chunk: string) => void): Promise<void> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.CHAT}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, stream: true }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body reader available');
    }

    const decoder = new TextDecoder();
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const content = line.slice(6); // Remove 'data: ' prefix
            if (content.trim()) {
              onChunk(content);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async getCommands(): Promise<{ commands: Command[] }> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.COMMANDS}`);
    if (!response.ok) {
      throw new Error('Failed to fetch commands');
    }
    return response.json();
  }

  async getConfig(): Promise<any> {
    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.CONFIG}`);
    if (!response.ok) {
      throw new Error('Failed to fetch config');
    }
    return response.json();
  }
}

export const apiService = new ApiService();
