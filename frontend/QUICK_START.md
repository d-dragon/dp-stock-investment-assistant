# Quick Start Guide - Frontend with Model Management

## Prerequisites
- Node.js 16+ installed
- Backend server configured with OpenAI API key
- npm or yarn package manager

## Installation

```bash
cd frontend
npm install
```

## Development Mode

### 1. Start Backend Server
```bash
# In project root
python src/main.py
# Backend should be running on http://localhost:5000
```

### 2. Start Frontend Development Server
```bash
# In frontend directory
npm start
# Frontend will open at http://localhost:3000
```

## Using the Model Selector

### In the UI
1. **View Models** - The model selector in the header shows available OpenAI models
2. **Select Model** - Click dropdown to choose a different model
3. **Refresh Models** - Click the refresh button (↻) to fetch latest models from OpenAI
4. **Current Selection** - The currently selected model is displayed in the dropdown

### Model Selection Workflow
```
User Flow:
┌─────────────────┐
│ Open App        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Models Load     │ ← Fetches from cache by default
│ Automatically   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User Selects    │
│ Model           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Backend Updates │
│ Selection       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Future Chats    │
│ Use New Model   │
└─────────────────┘
```

## Features Overview

### 1. Chat Interface
- Type messages in the input area
- Press Enter or click Send
- Streaming responses appear in real-time
- Cancel button stops ongoing streams

### 2. Model Management (NEW)
- **Model Selector Dropdown**: Choose from available models
- **Refresh Button**: Update model list from OpenAI API
- **Cache Indicator**: Shows if models loaded from cache (💾) or API (🌐)
- **Real-time Switching**: Change models without restart

### 3. Provider Override
- Additional dropdown for provider selection
- Options: Auto, OpenAI, Grok (stub)
- Useful for testing different providers

### 4. Connection Status
- Online/Offline indicator in header
- Automatic health check on startup
- Connection monitoring

## API Integration

### Endpoints Used by Frontend

#### Core Chat
```javascript
POST /api/chat
Body: { message: "...", stream: true, provider: "openai" }
Response: Server-Sent Events stream
```

#### Model Management
```javascript
// List models (cached)
GET /api/models/openai
Response: { models: [...], source: "cache", cached: true }

// Refresh models
POST /api/models/openai/refresh
Response: { models: [...], source: "openai", cached: false }

// Get current selection
GET /api/models/openai/selected
Response: { provider: "openai", name: "gpt-4" }

// Select model
POST /api/models/openai/select
Body: { provider: "openai", name: "gpt-4o-mini" }
Response: { provider: "openai", name: "gpt-4o-mini" }
```

## Code Structure

### Key Components
```typescript
// ModelSelector Component
import ModelSelector from './components/models/ModelSelector';

// Usage - Compact mode (header)
<ModelSelector compact onModelChange={handleChange} />

// Usage - Full mode (settings panel)
<ModelSelector onModelChange={handleChange} />
```

### API Service
```typescript
// Models API
import { modelsApi } from './services/modelsApi';

// List models
const models = await modelsApi.listModels(refresh=false);

// Select model
await modelsApi.selectModel({ 
  provider: 'openai', 
  name: 'gpt-4o-mini' 
});
```

### Type Definitions
```typescript
import { 
  OpenAIModel, 
  ModelListResponse, 
  ModelSelection 
} from './types/models';
```

## Environment Configuration

### .env File
```bash
# API Base URL (default: http://localhost:5000)
REACT_APP_API_URL=http://localhost:5000

# WebSocket URL (default: http://localhost:5000)
REACT_APP_WS_URL=http://localhost:5000
```

## Build & Deploy

### Production Build
```bash
npm run build
```

Output: `build/` directory ready for deployment

### Build Analysis
```bash
npm run build:analyze
```

### Serve Production Build Locally
```bash
npx serve -s build
```

## Troubleshooting

### Models Not Loading
**Problem:** Model dropdown shows "No models available"

**Solutions:**
1. Verify backend is running on port 5000
2. Check backend has valid OpenAI API key
3. Click refresh button to fetch models
4. Check browser console for errors
5. Verify CORS is configured on backend

### Build Errors
**Problem:** `npm run build` fails

**Solutions:**
1. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
2. Clear build cache: `npm run clean`
3. Check for TypeScript errors: Look at error messages
4. Ensure all imports are correct

### Connection Issues
**Problem:** "Backend server not available" message

**Solutions:**
1. Start backend server: `python src/main.py`
2. Verify backend is on port 5000: `curl http://localhost:5000/api/health`
3. Check for port conflicts
4. Review backend logs for errors

### Model Selection Not Persisting
**Problem:** Selected model resets on page refresh

**Note:** This is expected behavior - model selection is stored on backend. The frontend fetches current selection on load. To make a model persistent:
1. Use the model selector to choose a model
2. Backend stores this selection
3. Selection persists across frontend refreshes
4. To change default permanently, update backend config

## Development Tips

### Hot Reload
- Frontend supports hot reload (changes reflect immediately)
- No need to restart dev server for code changes
- Browser will auto-refresh

### Debugging
```javascript
// Enable debug logging
localStorage.setItem('debug', '*');

// Check model API calls
console.log(await modelsApi.listModels());
```

### Adding New Models Provider
1. Update backend to support new provider
2. Add provider option to ModelSelector
3. Update type definitions in `types/models.ts`
4. Test with new provider endpoints

## Testing

### Manual Testing Checklist
- [ ] App loads without errors
- [ ] Backend connection successful (green indicator)
- [ ] Models load in dropdown
- [ ] Can select different model
- [ ] Refresh button updates list
- [ ] Chat messages work with selected model
- [ ] Error handling works (disconnect backend and retry)
- [ ] Loading states display correctly
- [ ] Provider override works

### Browser Testing
- Test in Chrome, Firefox, Safari, Edge
- Test responsive design (mobile view)
- Test with slow network (throttling)

## Performance

### Bundle Size
- Main JS: ~49 KB (gzipped)
- CSS: <1 KB (gzipped)
- Total: ~50 KB - very efficient!

### Optimization Tips
- Models list is cached on backend (1 hour TTL)
- Frontend caches model selection in component state
- Streaming reduces perceived latency
- Lazy loading for future enhancements

## Support

### Documentation
- **FRONTEND_ANALYSIS.md** - Detailed analysis
- **UI_IMPROVEMENTS.md** - All improvements explained
- **REFINEMENT_SUMMARY.md** - Executive summary
- **README.md** - Full documentation

### Logs
```bash
# Frontend console logs
Open browser DevTools → Console tab

# Backend logs
Check terminal where backend is running
```

## What's Next?

### Suggested Enhancements
1. Add model comparison feature
2. Show model pricing information
3. Track usage statistics per model
4. Add model performance metrics
5. Implement settings panel
6. Add dark mode
7. Export chat history
8. Add user preferences

---

**Happy Coding!** 🚀

For issues or questions, refer to the comprehensive documentation in:
- FRONTEND_ANALYSIS.md
- UI_IMPROVEMENTS.md  
- REFINEMENT_SUMMARY.md
