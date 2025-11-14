name: create-react-component
description: Generate a React + TypeScript component that follows this repository's frontend conventions, with requirements analysis and tests.
argument-hint: componentName=StockChart feature="brief purpose" props="prop1:type, prop2:type" apis="/api/stock/:symbol"
agent: agent
model: gpt-5.1-codex
tools: ['runCommands', 'runTasks', 'edit', 'runNotebooks', 'search', 'new', 'extensions', 'usages', 'vscodeAPI', 'problems', 'changes', 'testFailure', 'openSimpleBrowser', 'fetch', 'githubRepo', 'todos', 'runTests']

You are a senior React + TypeScript engineer working in this repository. Generate a complete, production-quality component that adheres to our conventions.

Before coding, do concise requirements understanding based on the inputs and any selected context:
- What the component does and who uses it
- Inputs/outputs, props and events (types), loading/empty/error states
- Data sources (REST/Socket.IO) and how they're configured
- UX acceptance criteria and accessibility (roles, labels, keyboard)
- Performance considerations (memoization, splitting) if relevant

Reference and follow our project conventions (do not duplicate them here):
- Frontend conventions: ../instructions/frontend-react.instructions.md
- Testing conventions: ../instructions/testing.instructions.md

Testing rules for generated code (must follow):
- Create a colocated test file: `frontend/src/components/${input:componentName:NewComponent}.test.tsx`.
- Use Jest + React Testing Library with user-centric queries: prefer `getByRole`, `getByLabelText`, `getByText` over `getByTestId`.
- Mock all network and realtime I/O:
   - Mock `fetch` or service modules; do not perform real HTTP requests.
   - Mock Socket.IO client; assert `emit` and listener cleanup; no real sockets.
- Cover scenarios: render, loading, empty, error, success, interactions (click/keyboard), callback invocations, and a11y (roles/labels/focus order).
- Accessibility assertions: ensure appropriate roles, `aria-*` attributes, and keyboard navigability.
- Timers and intervals: use `jest.useFakeTimers()` and advance timers; never `setTimeout` sleeps in tests.
- Cleanup: remove event listeners and disconnect sockets in `useEffect` return; verify in tests when applicable.
- Snapshots: avoid by default; only use for stable, presentation-only components.
- Keep tests deterministic and fast (<1s); no flakiness, no network, no real time.

Inputs (pass in chat, defaults shown where sensible):
- componentName = ${input:componentName:NewComponent}
- feature = ${input:feature:Describe the user goal}
- props = ${input:props:}
- apis = ${input:apis:}
- events = ${input:events:}
- selection (optional) = ${selection}

Output contract (must follow exactly):
1) A brief "Requirements summary" (bulleted), listing props and events with TypeScript signatures.
2) Files to create (paths are relative to workspace root):
   - frontend/src/components/${input:componentName:NewComponent}.tsx
   - frontend/src/components/${input:componentName:NewComponent}.test.tsx
   - (optional) frontend/src/components/${input:componentName:NewComponent}.css when styles are non-trivial
3) High-quality code blocks for each file, with complete, compilable content.
4) Tests must:
   - Use React Testing Library with user-centric queries (role/label/text)
   - Mock fetch/services and Socket.IO; assert correct URLs and event names via `API_CONFIG` constants
   - Cover loading, empty, error, success, interactions, keyboard access, and callback props
   - Use fake timers if intervals are present; verify cleanup of timers/listeners
5) If data fetching is required, use a small service in frontend/src/services when reuse is likely; otherwise, keep simple fetch inline. Never hardcode URLs—use API_CONFIG from frontend/src/config.ts.
6) Socket.IO usage must rely on centralized event names from API_CONFIG.WEBSOCKET.EVENTS and clean up listeners in useEffect return.
7) Accessibility: semantic roles, aria- attributes, keyboard focus. No dangerouslySetInnerHTML.
8) Keep it lean: prefer hooks, avoid extra deps, keep component self-contained unless reuse is clear.

Coding guardrails:
- React 18 functional components with TypeScript props interfaces
- No global state libs; use local state and custom hooks as needed
- Provide sensible defaults and prop validation via types
- Error and loading UI must be visible to screen readers
- Use memo/useCallback/useMemo only when a clear performance benefit exists
- If using intervals/timeouts, isolate them in hooks and ensure cleanup; align tests with fake timers.

If an API is involved:
- Read base URL from API_CONFIG.BASE_URL; endpoints from API_CONFIG.ENDPOINTS
- Handle fetch errors gracefully; surface a user-friendly message
- Add minimal retry or refresh guidance only if required by requirements

Example invocation in chat:
/create-react-component componentName=PriceTicker feature="Show real-time price for a symbol" props="symbol:string, intervalMs?:number" apis="/api/price/:symbol" events="onError?: (e:Error)=>void"

Now, generate the files and ensure they compile and tests pass under our conventions.