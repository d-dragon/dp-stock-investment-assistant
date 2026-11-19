// Empty means same origin. The Vite dev server proxies /api to port 5000.
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? ''

// API Configuration
export const API_CONFIG = {
  BASE_URL: apiBaseUrl,
  ENDPOINTS: {
    HEALTH: '/api/health',
    CHAT: '/api/chat',
    COMMANDS: '/api/commands',
    CONFIG: '/api/config'
  },
};

// UI Configuration
export const UI_CONFIG = {
  MESSAGES: {
    MAX_DISPLAY: 100,
    AUTO_SCROLL: true
  }
};
