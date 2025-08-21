import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { getUUID } from './utils/uuid';

// expose for legacy/global callers (optional)
;(window as any).getUUID = getUUID;

const container = document.getElementById('root')!;
const root = createRoot(container);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
