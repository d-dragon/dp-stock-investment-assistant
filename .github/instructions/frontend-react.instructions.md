---
description: Frontend conventions for React, TypeScript, Socket.IO, and component architecture
applyTo: "frontend/**"
---

# Frontend - React + TypeScript Conventions
## Design Principles
- **Single Responsibility**: Components render UI only; data fetching and state logic belong in custom hooks or services
- **Interface Segregation**: Keep props and service interfaces narrow; split hooks/services rather than creating monolithic clients
- **Open/Closed**: Extend functionality via new components/hooks/services; avoid modifying shared primitives or breaking existing contracts
- **Dependency Inversion**: Components depend on typed interfaces from `services/`; inject configuration from `config.ts`; never hardcode endpoints
- **Liskov Substitution**: Service implementations must maintain consistent return shapes, error semantics, and cancellation behavior (AbortController)
- **Composition over Mutation**: Favor composing existing components/hooks over editing shared code; extend API/WebSocket clients without breaking contracts

## Data Fetching and Streaming
- **Streaming**: Use `ReadableStream` for SSE, `AbortController` for cancellation; clean up subscriptions in `useEffect` return
- **Async Safety**: Guard state updates with `isMounted` refs to prevent updates after unmount
- **Service Layer**: Centralize all API/WebSocket logic in `services/`; components consume via custom hooks

## State and Caching
- **Local State First**: Use `useState`/`useReducer` for component state; lift only when necessary
- **Memoization**: Apply `useMemo`/`useCallback` when profiling shows benefit; avoid premature optimization
- **No Global Mutable State**: Use context or custom hooks; avoid singletons that hold mutable state

## Testing Strategy
- **Framework**: Jest + React Testing Library
- **Mock External Dependencies**: Mock API calls, WebSocket connections, SSE streams
- **Test User Behavior**: Test what users see and do, not internal state or implementation details
- **Deterministic Components**: Keep render logic pure; move side effects to hooks

## Styling and UX
- **Design Tokens**: Use theme constants from `config.ts`; no hardcoded colors or spacing
- **Accessibility**: Add ARIA labels, manage focus for modals/dialogs, ensure keyboard navigation
- **No Secrets in Code**: Never expose API keys or sensitive data in frontend code
## Tech Stack
- **Framework**: React 18.3+ with TypeScript
- **Build Tool**: Create React App (react-scripts 5.0+)
- **Real-time**: Socket.IO Client 4.8+ for chat streaming
- **Testing**: Jest + React Testing Library (via react-scripts)

## Project Structure
```
frontend/src/
├── components/       # React components (PascalCase files)
├── services/         # API wrappers, Socket.IO client, data fetching
├── types/            # Shared TypeScript types and interfaces
├── utils/            # Pure helper functions (validation, formatting)
├── config.ts         # API and UI configuration constants
├── App.tsx           # Root component
└── index.tsx         # Entry point
```

## Component Guidelines
- **Functional Components**: Use hooks exclusively; avoid class components
- **File Naming**: PascalCase for components (`StockChart.tsx`, `ChatMessage.tsx`)
- **Co-located Styles**: Keep component-specific CSS next to component if small (<100 lines)
- **Global Styles**: Only for resets, theme variables, and shared utilities (`index.css`)
- **Props Interface**: Define TypeScript interfaces for all component props
  ```typescript
  interface ChatMessageProps {
    message: string;
    timestamp: string;
    isUser: boolean;
  }
  export const ChatMessage: React.FC<ChatMessageProps> = ({ message, timestamp, isUser }) => { ... }
  ```

## State Management
- **Local State**: Use `useState`/`useReducer` for component-scoped state
- **Lifting State**: Only lift state when multiple components need shared access
- **Custom Hooks**: Encapsulate complex state logic and side effects
  - Example: `useChatStream()` for WebSocket message handling
  - Pattern: `use<Feature>` naming convention
- **Avoid Prop Drilling**: Use context or custom hooks for deeply nested state
- **No Global State Library**: Keep state simple with hooks; add Redux/Zustand only if complexity warrants

## Data Fetching and API Integration
- **API Service Layer**: Wrap all API calls in `services/` modules
- **Configuration**: Use `config.ts` for API base URLs and constants
  ```typescript
  export const API_CONFIG = {
    BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
    ENDPOINTS: { HEALTH: '/api/health', CHAT: '/api/chat' }
  };
  ```
- **Environment Variables**: Prefix with `REACT_APP_*` (e.g., `REACT_APP_API_URL`, `REACT_APP_WS_URL`)
- **Localhost Fallbacks**: Always provide sensible localhost defaults in `config.ts`
- **Never Hardcode URLs**: No production URLs in source code; use env vars

## WebSocket / Socket.IO Conventions
- **Single Client Instance**: One Socket.IO client per logical feature (e.g., chat)
- **Event Constants**: Centralize in `API_CONFIG.WEBSOCKET.EVENTS` to prevent typos
  ```typescript
  WEBSOCKET: {
    URL: process.env.REACT_APP_WS_URL || 'http://localhost:5000',
    EVENTS: {
      CONNECT: 'connect',
      DISCONNECT: 'disconnect',
      CHAT_MESSAGE: 'chat_message',
      CHAT_RESPONSE: 'chat_response',
      ERROR: 'error'
    }
  }
  ```
- **Cleanup Listeners**: Always remove event listeners in `useEffect` return
  ```typescript
  useEffect(() => {
    socket.on('chat_response', handleResponse);
    return () => { socket.off('chat_response', handleResponse); };
  }, []);
  ```
- **Connection Management**: Reconnect logic for dropped connections; display status to user

## Styling and Theming
- **Theme Constants**: Define palette in `UI_CONFIG.THEME` (config.ts)
  ```typescript
  export const UI_CONFIG = {
    THEME: {
      PRIMARY_COLOR: '#1976d2',
      SECONDARY_COLOR: '#388e3c',
      ERROR_COLOR: '#d32f2f',
      SUCCESS_COLOR: '#2e7d32'
    }
  };
  ```
- **No Magic Values**: Use theme constants instead of hardcoded hex colors
- **CSS Variables**: If expanding theming, consider CSS custom properties
- **Theme Provider**: Update guidelines if adopting Material-UI/Chakra/styled-components

## Performance Optimization
- **Memoization**: Use `React.memo`, `useCallback`, `useMemo` only when profiling indicates benefit
- **Code Splitting**: Split large features with `React.lazy` and dynamic `import()`
  ```typescript
  const StockChart = React.lazy(() => import('./components/StockChart'));
  ```
- **Bundle Analysis**: Run `npm run build:analyze` before adding heavy dependencies
- **Avoid Premature Optimization**: Profile first; optimize hot paths only

## Error Handling
- **Error Boundaries**: Use React Error Boundary to catch render errors
- **Toast/Notification System**: Surface API/WebSocket errors to user
- **No Silent Failures**: Log errors and display user-friendly messages
- **API Error Responses**: Parse backend error messages; don't expose raw stack traces
- **Limit Console Logs**: Use `console.log` only for local debugging; remove before commit

## Testing with Jest + React Testing Library
- **User-Centric Queries**: Prefer `getByRole`, `getByText`, `getByLabelText` over `getByTestId`
- **Accessibility Testing**: Use `getByRole` to ensure proper ARIA attributes
- **No Implementation Details**: Don't test state or internal functions; test user-visible behavior
- **Snapshot Tests**: Use sparingly for stable, presentation-heavy components
- **Mock Services**: Mock API calls and WebSocket connections
- **Run Tests**:
  - Local: `npm test` (watch mode)
  - CI: `npm run test:ci` (coverage, non-interactive)

## Build Scripts
- **Development**:
  - `npm run start` - Standard dev server with source maps
  - `npm run start:fast` - Disables source maps for quicker startup (set `GENERATE_SOURCEMAP=false`)
  - `npm run start:dev` - Explicit NODE_ENV=development
- **Production**:
  - `npm run build` - Optimized production build
  - `npm run build:analyze` - Build + bundle size breakdown
- **Testing**:
  - `npm test` - Watch mode
  - `npm run test:ci` - Coverage, CI-friendly
- **Utilities**:
  - `npm run clean` - Remove build artifacts and cache
  - `npm run benchmark` - Performance benchmarking
  - `npm run perf` - Performance monitoring

## Dependency Management
- **Keep Dependencies Lean**: Review bundle analyzer before adding new libs
- **Prefer Native APIs**: Use browser APIs (fetch, Intersection Observer) over polyfills when possible
- **Lightweight Utilities**: Avoid lodash/moment if native methods suffice
- **Lock File**: Commit `package-lock.json` for reproducible builds
- **Security Audits**: Run `npm audit` regularly; fix high/critical issues

## Accessibility (a11y)
- **Semantic HTML**: Use proper elements (`<button>`, `<nav>`, `<main>`)
- **ARIA Labels**: Add `aria-label`, `aria-describedby` for screen readers
- **Keyboard Navigation**: Ensure all interactive elements are keyboard accessible
- **Focus Management**: Use `autoFocus` and `useRef` to manage focus in modals/dialogs
- **Color Contrast**: Meet WCAG AA standards (test with browser DevTools)

## Security Best Practices
- **No `dangerouslySetInnerHTML`**: Never render unsanitized user input as HTML
- **Escape Rich Text**: Use DOMPurify if rendering markdown/HTML from backend
- **Env Secrets**: Frontend receives only public or proxy-safe values; never leak API keys
- **HTTPS in Production**: Ensure API and WebSocket URLs use `https://` and `wss://`
- **Content Security Policy**: Configure CSP headers in Nginx (production)

## Environment Variables
- **Prefix**: All env vars must start with `REACT_APP_*` (Create React App requirement)
- **Document New Vars**: Add to this file and README when introducing new env keys
- **Example `.env.local`**:
  ```env
  REACT_APP_API_URL=http://localhost:5000
  REACT_APP_WS_URL=http://localhost:5000
  ```

## CI/CD Considerations
- **Deterministic Tests**: No real network; mock all external services
- **Fast Feedback**: Use `npm run test:ci` with `--maxWorkers=2` for parallel execution
- **Fail Fast**: Set CI to fail on test failures, lint errors, and TypeScript errors
- **Build Verification**: Run `npm run build` in CI to catch production issues early

## Common Frontend Tasks
### Add a New Component
1. Create `<ComponentName>.tsx` in `frontend/src/components/`
2. Define props interface with TypeScript
3. Add tests in `<ComponentName>.test.tsx`
4. Export from parent directory `index.ts` if needed

### Add API Endpoint Integration
1. Update `config.ts` with new endpoint constant
2. Create service function in `services/` to wrap API call
3. Use service in component via custom hook or `useEffect`
4. Handle loading/error states

### Add WebSocket Event
1. Add event name to `API_CONFIG.WEBSOCKET.EVENTS`
2. Implement listener in service or custom hook
3. Clean up listener on unmount
4. Update backend Socket.IO handler to match event name

## Pitfalls and Gotchas
- **Unmounted Component Updates**: Always cleanup async operations in `useEffect` return
  ```typescript
  useEffect(() => {
    let isMounted = true;
    fetchData().then(data => { if (isMounted) setState(data); });
    return () => { isMounted = false; };
  }, []);
  ```
- **WebSocket Cleanup**: Remove all listeners on unmount to prevent memory leaks
  ```typescript
  useEffect(() => {
    socket.on('chat_response', handleResponse);
    return () => {
      socket.off('chat_response', handleResponse);
      socket.removeAllListeners();
    };
  }, []);
  ```
- **Infinite Loops**: Missing dependency array or stale closure in `useEffect`
- **Key Prop**: Always provide unique `key` for list items (use ID, not array index if list reorders)
- **Source Map Bloat**: Use `start:fast` for quicker local dev if source maps cause slowness

## Quick Sanity Checks
```powershell
cd frontend
npm install                  # Install dependencies
npm run start                # Dev server (http://localhost:3000)
npm run build                # Production build → build/
npm run build:analyze        # Bundle size breakdown
npm test                     # Run tests in watch mode
```

## References
- React Docs: https://react.dev/
- TypeScript Handbook: https://www.typescriptlang.org/docs/handbook/
- React Testing Library: https://testing-library.com/docs/react-testing-library/intro/
- Socket.IO Client: https://socket.io/docs/v4/client-api/
