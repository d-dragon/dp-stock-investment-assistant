import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './design-system/tokens/generated/tokens.css';
import './design-system/tokens/generated/fonts.css';


const container = document.getElementById('root')!;
const root = createRoot(container);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
