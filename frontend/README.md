# Stock Investment Assistant Frontend

This is the React frontend for the DP Stock Investment Assistant.

## Getting Started

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Features

- Real-time chat interface with the investment assistant
- **OpenAI model selection and management** (NEW)
  - View all available OpenAI models
  - Switch models in real-time
  - Refresh model catalog from OpenAI API
  - See current model selection
  - Cache status indicator
- Connection status monitoring
- Streaming chat responses
- Provider selection (OpenAI, Grok stub)
- Message history with metadata (provider, model, fallback status)
- Responsive design
- Modern UI with TypeScript and strict type checking

## Backend Requirements

Make sure the Flask backend is running on `http://localhost:5000` for the frontend to work properly.

## Application Design

### **Core Architecture**
The frontend is a **React 18.3.1 single-page application (SPA)** built with Create React App (`react-scripts 5.0.1`). It follows a modern component-based architecture designed for real-time interaction with an AI-powered stock investment assistant.

### **Directory Structure**
```
frontend/
├── public/                          # Static assets served directly
│   ├── index.html                  # Main HTML template with React mount point
│   └── manifest.json               # PWA configuration
├── src/                            # Source code
│   ├── components/                 # React components
│   │   ├── models/                 # Model management components
│   │   │   └── ModelSelector.tsx   # OpenAI model selector (NEW)
│   │   ├── WebSocketTest.tsx       # WebSocket testing component
│   │   └── ...                     # Other components
│   ├── services/                   # API services
│   │   ├── modelsApi.ts           # Model management API (NEW)
│   │   ├── restApiClient.js       # REST API client with streaming
│   │   ├── apiService.ts          # TypeScript API service
│   │   └── webSocketService.ts    # Socket.IO service
│   ├── types/                      # TypeScript type definitions
│   │   └── models.ts              # Model-related types (NEW)
│   ├── utils/                      # Utility functions
│   │   └── uuid.ts                # UUID generation
│   ├── App.tsx                    # Main React component (chat interface)
│   ├── App.css                    # Component styling
│   ├── index.tsx                  # React application entry point
│   ├── index.css                  # Global styles and base layout
│   └── config.ts                  # Configuration constants
├── package.json                    # Dependencies and build scripts
├── tsconfig.json                   # TypeScript configuration
├── .env                           # Environment configuration
├── ../docs/domains/frontend/FRONTEND_ANALYSIS.md   # Analysis and refinement plan (moved)
├── ../docs/domains/frontend/UI_IMPROVEMENTS.md     # Improvements documentation (moved)
└── node_modules/                   # NPM dependencies (git-ignored)
```

### **Application Purpose**

#### **Primary Function**
- **AI-Powered Investment Assistant**: Real-time chat interface for stock analysis, investment strategies, and market insights
- **Backend Integration**: Communicates with Flask API server on `localhost:5000`
- **User Experience**: Conversational interface for financial advice and analysis

#### **Key Features**
1. **Real-time Chat Interface**
   - Message exchange with AI assistant
   - Loading states with animated indicators
   - Message history persistence during session

2. **Connection Management**
   - Health check monitoring (`/api/health` endpoint)
   - Connection status indicator (🟢/🔴)
   - Automatic retry and refresh capabilities

3. **Responsive Design**
   - Mobile-first approach with breakpoints
   - Gradient background theme (`#667eea` to `#764ba2`)
   - Glassmorphism UI effects with backdrop blur

### **Software Stack**

#### **Frontend Technologies**
- **React 18.3.1**: Modern hooks-based component architecture
- **TypeScript**: Full type safety with strict mode enabled
- **React DOM 18.3.1**: Virtual DOM rendering with `createRoot`
- **React Scripts 5.0.1**: Build tooling, development server, and bundling
- **Socket.IO Client 4.8.1**: Real-time WebSocket communication
- **CSS3**: Advanced styling with gradients, animations, and responsive design
- **Fetch API**: HTTP client for backend communication# Stock Investment Assistant Frontend

This is the React frontend for the DP Stock Investment Assistant.

## Getting Started

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Features

- Real-time chat interface with the investment assistant
- **OpenAI model selection and management** (NEW)
  - View all available OpenAI models
  - Switch models in real-time
  - Refresh model catalog from OpenAI API
  - See current model selection
  - Cache status indicator
- Connection status monitoring
- Streaming chat responses
- Provider selection (OpenAI, Grok stub)
- Message history with metadata (provider, model, fallback status)
- Responsive design
- Modern UI with TypeScript and strict type checking

## Backend Requirements

Make sure the Flask backend is running on `http://localhost:5000` for the frontend to work properly.

## Application Design

### **Core Architecture**
The frontend is a **React 18.3.1 single-page application (SPA)** built with Create React App (`react-scripts 5.0.1`). It follows a modern component-based architecture designed for real-time interaction with an AI-powered stock investment assistant.

### **Directory Structure**
```
frontend/
├── public/                          # Static assets served directly
│   ├── index.html                  # Main HTML template with React mount point
│   └── manifest.json               # PWA configuration
├── src/                            # Source code
│   ├── components/                 # React components
│   │   ├── models/                 # Model management components
│   │   │   └── ModelSelector.tsx   # OpenAI model selector (NEW)
│   │   ├── WebSocketTest.tsx       # WebSocket testing component
│   │   └── ...                     # Other components
│   ├── services/                   # API services
│   │   ├── modelsApi.ts           # Model management API (NEW)
│   │   ├── restApiClient.js       # REST API client with streaming
│   │   ├── apiService.ts          # TypeScript API service
│   │   └── webSocketService.ts    # Socket.IO service
│   ├── types/                      # TypeScript type definitions
│   │   └── models.ts              # Model-related types (NEW)
│   ├── utils/                      # Utility functions
│   │   └── uuid.ts                # UUID generation
│   ├── App.tsx                    # Main React component (chat interface)
│   ├── App.css                    # Component styling
│   ├── index.tsx                  # React application entry point
│   ├── index.css                  # Global styles and base layout
│   └── config.ts                  # Configuration constants
├── package.json                    # Dependencies and build scripts
├── tsconfig.json                   # TypeScript configuration
├── .env                           # Environment configuration
├── ../docs/domains/frontend/FRONTEND_ANALYSIS.md   # Analysis and refinement plan (moved)
├── ../docs/domains/frontend/UI_IMPROVEMENTS.md     # Improvements documentation (moved)
└── node_modules/                   # NPM dependencies (git-ignored)
```

### **Application Purpose**

#### **Primary Function**
- **AI-Powered Investment Assistant**: Real-time chat interface for stock analysis, investment strategies, and market insights
- **Backend Integration**: Communicates with Flask API server on `localhost:5000`
- **User Experience**: Conversational interface for financial advice and analysis

#### **Key Features**
1. **Real-time Chat Interface**
   - Message exchange with AI assistant
   - Loading states with animated indicators
   - Message history persistence during session

2. **Connection Management**
   - Health check monitoring (`/api/health` endpoint)
   - Connection status indicator (🟢/🔴)
   - Automatic retry and refresh capabilities

3. **Responsive Design**
   - Mobile-first approach with breakpoints
   - Gradient background theme (`#667eea` to `#764ba2`)
   - Glassmorphism UI effects with backdrop blur

### **Software Stack**

#### **Frontend Technologies**
- **React 18.3.1**: Modern hooks-based component architecture
- **TypeScript**: Full type safety with strict mode enabled
- **React DOM 18.3.1**: Virtual DOM rendering with `createRoot`
- **React Scripts 5.0.1**: Build tooling, development server, and bundling
- **Socket.IO Client 4.8.1**: Real-time WebSocket communication
- **CSS3**: Advanced styling with gradients, animations, and responsive design
- **Fetch API**: HTTP client for backend communication

#### **Development Stack**
- **Node.js**: JavaScript runtime environment
- **NPM**: Package management and dependency resolution
- **Create React App**: Zero-configuration build setup
- **ESLint**: Code quality and consistency
- **Babel**: JavaScript transpilation for browser compatibility

#### **Backend Integration**
- **Flask API**: Python backend on `localhost:5000`
- **RESTful Endpoints**:
  - `GET /api/health` - Connection health check
  - `POST /api/chat` - Message processing and AI responses (supports streaming)
  - `GET /api/config` - Configuration retrieval
  - `GET /api/models/openai` - List available OpenAI models (cached)
  - `POST /api/models/openai/refresh` - Refresh model catalog
  - `GET /api/models/openai/selected` - Get current model selection
  - `POST /api/models/openai/select` - Select a model
  - `PUT /api/models/openai/default` - Set default model
- **JSON Communication**: Structured data exchange
- **Server-Sent Events (SSE)**: Streaming chat responses

### **Key Components Analysis**

#### **App.js (Main Component)**
```javascript
// State Management
const [messages, setMessages] = useState([]);        // Chat history
const [inputValue, setInputValue] = useState('');    // User input
const [isConnected, setIsConnected] = useState(false); // Backend status
const [isLoading, setIsLoading] = useState(false);   // Processing state
```

**Features:**
- **Message Flow**: User input → API call → AI response → UI update
- **Error Handling**: Connection failures, HTTP errors, timeout handling
- **UI Interactions**: Keyboard shortcuts (Enter to send), disabled states
- **Auto-scroll**: Maintains scroll position at latest message

#### **Styling Architecture (App.css)**
- **Modern CSS**: Flexbox layouts, CSS Grid, custom properties
- **Visual Effects**: Glassmorphism, backdrop filters, smooth animations
- **Responsive Design**: Mobile breakpoints at 768px
- **Loading Animations**: Keyframe animations for processing indicators

### **Performance Considerations**

#### **Optimization Features**
- **React.StrictMode**: Development mode debugging
- **Component Optimization**: Functional components with hooks
- **Minimal Bundle**: Only essential dependencies included
- **Lazy Loading**: Efficient rendering with `useRef` and `useEffect`

#### **Browser Compatibility**
- **Modern Browsers**: Supports latest Chrome, Firefox, Safari, Edge
- **Fallback Support**: Graceful degradation for older browsers
- **Progressive Enhancement**: Core functionality works without JavaScript

### **Security & Best Practices**

#### **Security Measures**
- **CORS Handling**: Backend must configure appropriate CORS policies
- **Input Validation**: Client-side validation before API calls
- **Error Boundaries**: Graceful error handling and user feedback

#### **Development Practices**
- **Environment Configuration**: `.env` files for environment-specific settings
- **Git Ignore**: `node_modules`, build artifacts, and sensitive files excluded
- **Linting**: ESLint configuration for code quality
- **Component Architecture**: Single responsibility principle, reusable components

### **Deployment Readiness**

#### **Production Build**
- **Build Process**: `npm run build` creates optimized production bundle
- **Asset Optimization**: Minification, tree-shaking, code splitting
- **Static Hosting**: Can be deployed to Netlify, Vercel, GitHub Pages, or CDN

#### **PWA Capabilities**
- **Manifest.json**: Progressive Web App configuration
- **Service Worker Ready**: Can be extended for offline functionality
- **Mobile Optimization**: Responsive design with touch-friendly interactions

### **Integration Points**

#### **Backend Dependencies**
- **Flask Server**: Must be running on `localhost:5000`
- **API Endpoints**: Health check and chat processing required
- **Data Format**: JSON request/response structure
- **Error Handling**: Proper HTTP status codes and error messages

This frontend application represents a modern, production-ready React SPA designed specifically for AI-powered financial consultation, with emphasis on real-time interaction, responsive design, and seamless backend integration.
