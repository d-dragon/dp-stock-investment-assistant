// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  ENDPOINTS: {
    HEALTH: '/api/health',
    CHAT: '/api/chat',
    COMMANDS: '/api/commands',
    CONFIG: '/api/config'
  },
  WEBSOCKET: {
    URL: process.env.REACT_APP_WS_URL || 'http://localhost:5000',
    EVENTS: {
      CONNECT: 'connect',
      DISCONNECT: 'disconnect',
      CHAT_MESSAGE: 'chat_message',
      CHAT_RESPONSE: 'chat_response',
      ERROR: 'error',
      STATUS: 'status'
    }
  }
};

// UI Configuration
export const UI_CONFIG = {
  THEME: {
    PRIMARY_COLOR: '#1976d2',
    SECONDARY_COLOR: '#388e3c',
    ERROR_COLOR: '#d32f2f',
    SUCCESS_COLOR: '#2e7d32'
  },
  MESSAGES: {
    MAX_DISPLAY: 100,
    AUTO_SCROLL: true
  }
};
