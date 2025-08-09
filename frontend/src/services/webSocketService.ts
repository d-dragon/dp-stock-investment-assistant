import io from 'socket.io-client';

// Define the socket type from the returned io instance
type SocketIOClient = ReturnType<typeof io>;

export interface SocketMessage {
  message: string;
}

export interface SocketResponse {
  response: string;
  timestamp: string;
}

export interface SocketError {
  message: string;
}

export interface SocketStatus {
  message: string;
}

class WebSocketService {
  private socket: SocketIOClient | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isConnecting = false;

  connect(): Promise<SocketIOClient> {
    return new Promise((resolve, reject) => {
      if (this.socket?.connected) {
        resolve(this.socket);
        return;
      }

      if (this.isConnecting) {
        // Wait for current connection attempt
        setTimeout(() => {
          if (this.socket?.connected) {
            resolve(this.socket);
          } else {
            reject(new Error('Connection timeout'));
          }
        }, 5000);
        return;
      }

      this.isConnecting = true;

      try {
        this.socket = io('http://localhost:5000', {
          autoConnect: true,
          reconnection: true,
          reconnectionAttempts: this.maxReconnectAttempts,
          reconnectionDelay: this.reconnectDelay,
          transports: ['websocket', 'polling'], // Fallback to polling if websocket fails
          timeout: 10000,
          forceNew: false
        });

        this.setupEventHandlers();

        // Wait for connection
        this.socket.on('connect', () => {
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          console.log('WebSocket connected successfully');
          resolve(this.socket!);
        });

        this.socket.on('connect_error', (error: Error) => {
          this.isConnecting = false;
          console.error('WebSocket connection error:', error);
          reject(error);
        });

        // Manual connection if autoConnect fails
        if (!this.socket.connected) {
          this.socket.connect();
        }

      } catch (error) {
        this.isConnecting = false;
        console.error('Failed to create socket connection:', error);
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket.removeAllListeners();
      this.socket = null;
    }
    this.isConnecting = false;
    this.reconnectAttempts = 0;
  }

  async sendMessage(message: string): Promise<void> {
    if (!this.socket || !this.socket.connected) {
      try {
        await this.connect();
      } catch (error) {
        throw new Error(`Cannot send message: WebSocket not connected - ${error}`);
      }
    }

    if (this.socket?.connected) {
      this.socket.emit('chat_message', { message });
    } else {
      throw new Error('WebSocket is not connected');
    }
  }

  onConnect(callback: () => void): void {
    if (this.socket) {
      this.socket.on('connect', callback);
    }
  }

  onDisconnect(callback: (reason: string) => void): void {
    if (this.socket) {
      this.socket.on('disconnect', callback);
    }
  }

  onMessage(callback: (data: SocketResponse) => void): void {
    if (this.socket) {
      this.socket.on('chat_response', callback);
    }
  }

  onError(callback: (data: SocketError) => void): void {
    if (this.socket) {
      this.socket.on('error', callback);
    }
  }

  onStatus(callback: (data: SocketStatus) => void): void {
    if (this.socket) {
      this.socket.on('status', callback);
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  getConnectionState(): string {
    if (!this.socket) return 'disconnected';
    if (this.isConnecting) return 'connecting';
    if (this.socket.connected) return 'connected';
    return 'disconnected';
  }

  private setupEventHandlers(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.isConnecting = false;
    });

    this.socket.on('disconnect', (reason: string) => {
      console.log('WebSocket disconnected:', reason);
      this.isConnecting = false;
    });

    this.socket.on('connect_error', (error: Error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;
      this.isConnecting = false;
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached');
        this.disconnect();
      }
    });

    this.socket.on('reconnect', (attemptNumber: number) => {
      console.log('WebSocket reconnected after', attemptNumber, 'attempts');
      this.reconnectAttempts = 0;
    });

    this.socket.on('reconnect_error', (error: Error) => {
      console.error('WebSocket reconnection error:', error);
    });

    this.socket.on('reconnect_failed', () => {
      console.error('WebSocket reconnection failed');
      this.disconnect();
    });
  }
}

export const webSocketService = new WebSocketService();
