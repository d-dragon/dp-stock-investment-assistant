# 🚀 Complete Setup Guide: React.js UI for Stock Investment Assistant

This guide will help you set up a complete React.js frontend to communicate with your Python stock investment agent.

## 📋 What We've Built

### 1. **Backend API Server** (`src/web/api_server.py`)
- Flask web server that wraps your existing Python agent
- REST API endpoints for chat functionality
- WebSocket support for real-time communication
- CORS enabled for React frontend

### 2. **React Frontend** (`frontend/`)
- Clean, responsive chat interface
- Real-time communication with the backend
- Stock market query examples
- Connection status monitoring

## 🎯 Setup Instructions

### Step 1: Prepare the Backend

1. **Install Python dependencies:**
   ```bash
   pip install flask flask-cors flask-socketio
   ```

2. **Test the API server:**
   ```bash
   # From project root
   python src/web/api_server.py
   ```
   You should see: "🚀 Starting Stock Investment Assistant API Server..."

### Step 2: Setup the React Frontend

1. **Install Node.js** (if not already installed):
   - Download from https://nodejs.org/
   - Choose the LTS version
   - Verify: `node --version` and `npm --version`

2. **Install React dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```
   This will open http://localhost:3000 in your browser

### Step 3: Start Both Services

#### Option A: Use the Automated Script (Windows)
```bash
# From project root
start_app.bat
```
This will start both backend and frontend in separate windows.

#### Option B: Manual Start (Two terminals)
```bash
# Terminal 1: Backend
python src/web/api_server.py

# Terminal 2: Frontend  
cd frontend
npm start
```

## 🌐 How It Works

```
User Browser (localhost:3000)
       ↓ HTTP Requests
Flask API Server (localhost:5000)  
       ↓ Function Calls
Your Python Agent (StockAgent)
       ↓ API Calls  
OpenAI GPT API
```

### API Endpoints Available:

- `GET /api/health` - Check server status
- `POST /api/chat` - Send messages to the agent
- `GET /api/commands` - Get available commands
- `GET /api/config` - Get safe configuration info

### Frontend Features:

- **Chat Interface**: Type questions and get AI responses
- **Connection Status**: Shows if backend is running
- **Quick Commands**: Click examples to try different queries
- **Error Handling**: Clear error messages and recovery
- **Responsive Design**: Works on desktop and mobile

## 🔧 Configuration

### Environment Variables (`.env` file):
```bash
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4
# ... other variables
```

### Backend Configuration:
- **Host**: localhost
- **Port**: 5000
- **CORS**: Enabled for localhost:3000

### Frontend Configuration:
- **Host**: localhost  
- **Port**: 3000
- **API URL**: http://localhost:5000

## 💬 Usage Examples

Once both services are running, you can ask questions like:

- "What is the current price of AAPL?"
- "Analyze the tech sector performance"
- "Should I invest in renewable energy stocks?"
- "What are the best dividend stocks?"
- "Help me understand P/E ratios"

## 🚨 Troubleshooting

### Backend Issues:
```bash
# If you see import errors:
pip install -r requirements.txt

# If port 5000 is busy:
# Edit api_server.py line ~185: server.run(port=5001)
```

### Frontend Issues:
```bash
# If React won't start:
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start

# If you see dependency errors:
npm install react react-dom react-scripts
```

### Connection Issues:
- Make sure backend starts first (you should see "Running on http://localhost:5000")
- Check that frontend shows "✅ Connected" in the top-right
- Try clicking the "🔄 Refresh" button
- Check browser console (F12) for error messages

## 🎨 Customization

### To modify the UI:
- Edit `frontend/src/App.js`
- Styling is done with inline CSS for simplicity
- Colors and layout can be changed in the style objects

### To add new API endpoints:
- Edit `src/web/api_server.py`
- Add new routes in the `_register_routes()` method
- Update the frontend to call new endpoints

### To enhance the agent:
- Modify `src/core/agent.py`
- The `process_query()` method handles all user input
- Add data analysis, stock lookups, or other features

## 📁 Project Structure

```
dp-stock-investment-assistant/
├── src/
│   ├── core/
│   │   ├── agent.py          # Your main agent
│   │   ├── ai_client.py      # OpenAI integration
│   │   └── data_manager.py   # Data handling
│   ├── utils/
│   │   └── config_loader.py  # Configuration
│   └── web/
│       └── api_server.py     # Flask API server
├── frontend/
│   ├── src/
│   │   ├── App.js           # React main component
│   │   └── index.js         # React entry point
│   ├── package.json         # Dependencies
│   └── README.md           # Frontend docs
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables
├── setup_react.bat        # Frontend setup script
├── start_app.bat          # Start both services
└── README.md              # Main documentation
```

## 🎉 You're All Set!

Your stock investment assistant now has a modern web interface! Users can interact with your AI agent through a clean, responsive React.js frontend.

**Next Steps:**
- Customize the UI styling and branding
- Add more sophisticated stock data integration
- Implement user authentication if needed
- Deploy to a cloud platform for wider access

**Need Help?**
- Check the browser console (F12) for frontend errors
- Check the Python terminal for backend errors  
- Ensure your OpenAI API key is properly configured
- Verify both services are running on the correct ports
