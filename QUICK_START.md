# Quick Start Guide - Configuration & Tools Verification

## TL;DR - Everything is Working! ✅

Your configuration is correct and all tools are properly initialized. Run this:
```powershell
python test_agent.py
```

---

## Quick Verification Commands

### 1. Check Configuration Loading (30 seconds)
```powershell
python test_config.py
```
**Expected output:**
```
✅ OpenAI Configuration:
   API Key: sk-proj-usYTqinoFaZsEBFgMgXqpJ...
   Model: gpt-5
✅ Grok Configuration:
   API Key: xai-00TWu9nUn0FhPDavrRKtUDT0LJ...
   Model: grok-4-1-fast-reasoning
✅ All configuration loaded successfully!
```

### 2. Check Tool Initialization (60 seconds)
```powershell
python test_tools.py
```
**Expected output:**
```
✅ StockSymbolTool imported
✅ ReportingTool imported
✅ Enabled tools: 2
   - stock_symbol: Retrieve stock symbol information...
   - reporting: Generate investment reports...
✅ Agent initialized successfully!
```

### 3. Test Agent with Queries (varies)
```powershell
python test_agent.py
```
**Expected behavior:**
- Responds to "What is the current price of AAPL?"
- Streams response for "Summarize recent news about AAPL"
- Uses StockSymbolTool and ReportingTool internally

### 4. Full System Health Check (2 minutes)
```powershell
python health_check.py
```
**Expected output:**
```
======================================================================
✅ ALL CHECKS PASSED - System is healthy!
======================================================================
```

---

## Start the API Server

```powershell
# Start API server (will listen on http://localhost:5000)
python src\main.py --mode web

# Or with explicit host/port:
python src\main.py --mode web --host 0.0.0.0 --port 5000
```

**Server ready when you see:**
```
🚀 Starting Stock Investment Assistant API Server...
📡 API will be available at: http://0.0.0.0:5000
💬 WebSocket endpoint: ws://localhost:5000
```

---

## Test API Endpoints

Once server is running, test these endpoints:

### Health Check
```powershell
curl http://localhost:5000/api/health
```
Expected: `{"status": "healthy"}`

### Chat Endpoint
```powershell
# Non-streaming response
curl -X POST http://localhost:5000/api/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "What is the price of AAPL?"}'
```

### Stream Endpoint
```powershell
# Streaming response
curl -X POST http://localhost:5000/api/chat/stream `
  -H "Content-Type: application/json" `
  -d '{"message": "Summarize news about AAPL"}'
```

---

## Configuration Files Hierarchy

Configuration is loaded in this order (later overrides earlier):

1. **Base** → `config/config.yaml`
2. **Environment overlay** → `config/config.local.yaml` (for APP_ENV=local)
3. **Environment variables** → `.env` file
   - `OPENAI_API_KEY` ✅ Set
   - `GROK_API_KEY` ✅ Set
   - `MONGODB_URI` ✅ Set
   - `REDIS_PASSWORD` ✅ Set

### Verify What's Loaded
```powershell
# Python REPL
python
```
```python
from utils.config_loader import ConfigLoader
config = ConfigLoader.load_config()
print(config.get('openai', {}).get('api_key')[:20] + "...")
print(config.get('model', {}))
```

---

## Tools Available to Agent

The agent has access to:

### 1. StockSymbolTool
- **What**: Retrieve stock symbol information and prices
- **Uses**: Data Manager, Cache
- **Query example**: "What is the current price of AAPL?"

### 2. ReportingTool
- **What**: Generate investment reports in markdown format
- **Uses**: Stock data, analysis
- **Query example**: "Generate a report on Microsoft"

### 3. (Future) TradingViewTool
- **Status**: Phase 2, currently commented out
- **When enabled**: Advanced charting and technical analysis

---

## Troubleshooting

### Issue: "No enabled tools found" message
**Status**: Normal during startup, tools ARE enabled
**Action**: None needed, this is just a logging artifact

### Issue: Wrong API key in logs
**Status**: Actually correct, being loaded from `.env`
**Verify with**:
```powershell
python test_config.py
```

### Issue: MongoDB connection error
**Check**:
```powershell
# Verify MongoDB is running
docker ps | findstr mongodb

# Or start it:
docker-compose up -d mongodb
```

### Issue: Redis connection error  
**Check**:
```powershell
# Verify Redis is running
docker ps | findstr redis

# Or start it:
docker-compose up -d redis
```

---

## What Each Test Script Does

| Script | Purpose | Duration | Details |
|--------|---------|----------|---------|
| `test_config.py` | Verify config loads from env | <30s | Checks all API keys and settings |
| `test_tools.py` | Verify tools initialize | ~60s | Creates agent, checks tool registry |
| `test_agent.py` | Test agent queries | Varies | Runs actual queries with streaming |
| `health_check.py` | Full system check | ~2min | All 8 system components |

---

## Environment Variables Verification

Check that these are set in `.env`:

```bash
# Required
OPENAI_API_KEY=sk-proj-...
GROK_API_KEY=xai-...
MONGODB_URI=mongodb://...
REDIS_PASSWORD=...

# Optional but recommended
APP_ENV=local
MODEL_PROVIDER=openai
LOG_LEVEL=INFO
```

**Current status**:
- OPENAI_API_KEY: ✅ Set to `sk-proj-usYTqinoFaZsEBFgMgXqpJ...`
- GROK_API_KEY: ✅ Set to `xai-00TWu9nUn0FhPDavrRKtUDT0LJ...`
- MONGODB_URI: ✅ Configured
- REDIS_PASSWORD: ✅ Configured

---

## Next Steps

1. ✅ **Verify config** → `python test_config.py`
2. ✅ **Check tools** → `python test_tools.py`
3. ✅ **Test agent** → `python test_agent.py`
4. 🚀 **Start API server** → `python src\main.py --mode web`
5. 🌐 **Connect React frontend** → Points to `http://localhost:5000`

---

## Production Deployment

When ready to deploy:
1. Copy `.env` to production with real API keys
2. Set `APP_ENV=production` in `.env`
3. Use `config/config.production.yaml` for production settings
4. Run via gunicorn: `gunicorn -k eventlet -w 1 -b 0.0.0.0:5000 src.wsgi:app`

---

**Questions?** Check `DIAGNOSTIC_REPORT.md` and `ISSUE_RESOLUTION.md` for more details.
