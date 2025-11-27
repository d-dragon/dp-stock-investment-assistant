# DP Stock-Investment Assistant

[TOC]

An AI-powered assistant for stock investment analysts, leveraging OpenAI's GPT API to provide market insights, answer financial queries, and analyze stock data.

## Features

- **Natural Language Q&A:** Ask questions about stocks, market trends, or financial reports.
- **Stock Data Analysis:** Integrate with financial APIs to analyze historical and real-time data.
- **Earnings Summaries:** Summarize key points from earnings releases and news.
- **Portfolio Suggestions:** Get AI-generated investment ideas and portfolio optimizations.
- **Import Stock Data:** Easily import stock data from various sources for analysis.
- **AI Model Configuration:** Set custom parameters and configuration options for AI models to tailor analysis and recommendations.
- **Set Analyzing Targets/Goals:** Define specific stocks, sectors, or financial metrics to focus analysis on your investment objectives.
- **Export Report:** Generate and export analysis reports in formats such as PDF, CSV, or markdown for sharing and documentation.

## Getting Started

### Prerequisites

- Python 3.8+
- [OpenAI API key](https://platform.openai.com/)
- (Optional) Financial data API keys (e.g., Yahoo Finance, Alpha Vantage)

### Installation

```bash
git clone https://github.com/d-dragon/dp-stock-investment-assistant.git
cd dp-stock-investment-assistant
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Configuration

There are two ways to configure the application:

#### Method 1: Using YAML Configuration File

1. Copy `config/config_example.yaml` to `config/config.yaml`
2. Fill in your API keys and customize settings in the YAML file

#### Method 2: Using Environment Variables (Recommended)

1. Copy `.env.example` to `.env`
2. Fill in your environment variables in the `.env` file

```bash
# Copy the example files
copy config\config_example.yaml config\config.yaml  # Windows
copy .env.example .env                               # Windows

# OR on Unix/macOS:
# cp config/config_example.yaml config/config.yaml
# cp .env.example .env
```

The application supports environment variable overrides, which means:

- Values in `.env` will override corresponding values in `config.yaml`
- System environment variables will override `.env` values
- This provides flexibility for different deployment environments

#### Required Environment Variables

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

#### Optional Environment Variables

```bash
# OpenAI Configuration
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# Financial APIs
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
ALPHA_VANTAGE_ENABLED=false
YAHOO_FINANCE_ENABLED=true

# Application Settings
APP_LOG_LEVEL=INFO
APP_CACHE_ENABLED=true
APP_MAX_HISTORY=100
```

See `.env.example` for a complete list of available environment variables.

### Usage

Run the main agent:

```bash
python src/main.py
```

## API Architecture

The application implements a **modular blueprint-based Flask architecture** for clean separation of concerns and maintainable code organization.

### Blueprint Structure
- **Core API Endpoints** (`src/web/routes/api_routes.py`):
  - `GET /api/health` - Service health check
  - `POST /api/chat` - Chat with the AI assistant (supports streaming)
  - `GET /api/config` - Get safe configuration details

- **Model Management Endpoints** (`src/web/routes/models_routes.py`):
  - `GET /api/models/openai` - List available OpenAI models (cached)
  - `POST /api/models/openai/refresh` - Refresh models cache from OpenAI API
  - `GET /api/models/openai/selected` - Get currently selected model
  - `POST /api/models/openai/select` - Select a model for use
  - `PUT /api/models/openai/default` - Set the default model used by the assistant

- **Socket.IO Integration** (`src/web/sockets/`):
  - Real-time WebSocket communication for chat streaming
  - Events: `connect`, `disconnect`, `chat_message`

### Dependency Injection
The architecture uses **immutable dataclasses** for dependency injection:
- `APIRouteContext` - Provides access to Flask app, agent, config, and utility functions
- `SocketIOContext` - Provides Socket.IO-specific dependencies and handlers

### Key Benefits
- **Modular Organization**: Clear separation between core API and model management
- **Clean Dependencies**: Immutable context objects prevent side effects
- **Testable Architecture**: Each blueprint can be tested in isolation
- **Scalable Design**: Easy to add new endpoint groups as separate blueprints

See `docs/openapi.yaml` for complete API specification with request/response schemas.

## Roadmap

- [ ] Basic GPT-powered Q&A
- [ ] Stock data integration
- [ ] Report summarization
- [ ] Portfolio suggestion engine
- [ ] Stock data import feature
- [ ] AI model configuration interface
- [ ] Set analysis targets/goals
- [ ] Export report feature

## Testing

Follow these concise steps to run the project tests locally (Windows PowerShell examples included).

### Prerequisites
- Python 3.8+
- Install project dependencies:
```powershell
python -m pip install -r requirements.txt
```
- Create a local env file from the example:
```powershell
copy .env.example .env
```

### Test Structure
The project uses **pytest** as the testing framework with the following test organization:
- **API Endpoint Tests**: Located in `tests/api/` directory
  - `api_endpoints.py` - Tests core API endpoints (health, chat, config) - 8 tests
  - `test_models_routes.py` - Tests model management endpoints - 9 tests  
- **Unit Tests**: Located in `tests/` directory for core functionality
- **Test Coverage**: 17 API endpoint tests providing full coverage of REST API functionality

### Quick Manual Checks
- Run the interactive agent:
```powershell
python src\main.py
```
- Simple streaming snippet (Python REPL or a script):
```python
from core.agent import StockAgent
from core.data_manager import DataManager
from utils.config_loader import ConfigLoader

cfg = ConfigLoader.load_config()
dm = DataManager(cfg)
agent = StockAgent(cfg, dm)
for chunk in agent.process_query_streaming("Latest news on AAPL"):
    print(chunk, end="", flush=True)
```

### Running Tests
Tests use pytest and lightweight stubs/mocks to avoid real API calls.

**Run all tests:**
```powershell
python -m pytest
```

**Run specific test categories:**
```powershell
# API endpoint tests only
python -m pytest tests/api/ -v

# Core functionality tests
python -m pytest tests/test_agent.py tests/test_model_factory.py -v

# Single test file
python -m pytest tests/api/api_endpoints.py -v
```

**Run with verbose output:**
```powershell
python -m pytest -v
```

### Key Test Types
- **Model factory selection & caching**: Validates model client creation and caching behavior
- **Agent fallback behavior**: Tests primary model failure scenarios and fallback mechanisms  
- **API endpoint validation**: Comprehensive testing of all REST API endpoints
- **Blueprint architecture**: Tests the modular blueprint-based route organization
- **Streaming generator behavior**: Validates real-time chat response streaming
- **Configuration management**: Tests model selection and configuration updates

### Test Environment Setup
Ensure `src` is on PYTHONPATH for imports (VS Code handles this automatically):
```powershell
$env:PYTHONPATH = "$PWD\src"
pytest -v
```

### Debugging & CI Tips
- Enable logging to inspect prompts and fallback behavior:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
- Use `MODEL_DEBUG_PROMPT=true` in `.env` to print prompts (do not enable in production)
- In CI, run pytest and linting; mock external services (OpenAI, data APIs) or use recorded HTTP playback (vcrpy)

### VS Code Integration
- Set the Python interpreter to use the project's virtual environment
- Add `PYTHONPATH` pointing to `${workspaceFolder}/src` in VS Code settings
- Use the Test Explorer to run/debug individual tests
- Tests are automatically discovered in the `tests/` directory

### Test Architecture Notes
- **No real API keys required** - All tests use mock clients and stub implementations
- **Blueprint testing** - Tests validate the modular Flask blueprint architecture
- **Dataclass compatibility** - Tests use `dataclasses.replace()` for immutable context updates
- **Isolated Flask apps** - Each test group uses isolated Flask application instances to prevent conflicts

---
## DB setup and migration

Checklist
 - Add or verify MongoDB and Redis services are available
 - Configure connection strings and credentials in `.env` or `config/config.yaml`
 - Run the migration script to create collections, indexes, and validation

This section documents how to set up MongoDB and Redis for local development or Docker, and how to run the project's migration that creates the necessary collections, indexes, and validation rules.

Prerequisites
 - Python 3.8+
 - Docker & Docker Compose (recommended)
 - MongoDB 5.0+ (local or container)
 - Redis 6.0+ (local or container)

Option 1 — Docker Compose (recommended)

1. Start MongoDB and Redis using Docker Compose:

```powershell
docker-compose up -d mongodb redis
```

2. Verify containers are running:

```powershell
docker-compose ps
```

3. Inspect container logs if needed:

```powershell
docker-compose logs mongodb
docker-compose logs redis
```

Option 2 — Local installations

1. Install MongoDB from https://www.mongodb.com/try/download/community and start the service.
2. Install Redis from https://redis.io/download and start the server.

Configuration

You can configure the services either via `config/config.yaml` or environment variables in a `.env` file (env overrides take precedence).

Add the following (example) to your `.env` file:

```powershell
# MongoDB
MONGODB_URI=mongodb://stockadmin:stockpassword@localhost:27017/stock_assistant?authSource=stock_assistant
MONGODB_DB_NAME=stock_assistant
MONGODB_USERNAME=stockadmin
MONGODB_PASSWORD=stockpassword

# If your host blocks port 27017 (common on some Windows setups), use an alternate host port
# outside the Windows excluded port ranges (example below uses `27034`). Update the URI accordingly:
# MONGODB_URI=mongodb://stockadmin:stockpassword@localhost:27034/stock_assistant?authSource=stock_assistant

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redispassword
REDIS_SSL=false
```

Data migration / initial DB setup

1. Run the migration script which creates collections, adds indexes and applies validation:

```powershell
python src/data/migration/db_setup.py
```

2. Verify collections in MongoDB:

```powershell
mongosh "${env:MONGODB_URI}"
# inside mongosh
show collections
db.symbols.getIndexes()
```

Collections created by migrations now include:

- Core market data: `market_data` (time-series), `symbols`, `fundamental_analysis`, `investment_reports`, `news_events`, `technical_indicators`, `market_snapshots`
- User + org context: `groups`, `users`, `user_profiles`, `accounts`, `user_preferences`, `investment_styles`, `strategies`, `rules_policies`
- Workspace artifacts: `workspaces`, `sessions`, `watchlists`, `investment_ideas`, `notes`, `tasks`, `analyses`, `reports`, `chats`, `notifications`
- Portfolio data: `portfolios`, `positions`, `trades`

See `docs/data_model_design.md` for a full breakdown of each collection, relationships, and implementation notes.

Troubleshooting

- Authentication errors: verify `.env` values match the DB user credentials and `authSource` is correct.
- Container issues: check `docker-compose logs mongodb` or `docker-compose ps`.
- Migration errors: ensure the DB user has permissions to create collections and indexes.

Backup and restore

MongoDB backup:

```powershell
docker-compose exec mongodb mongodump --db stock_assistant --out /backup
```

MongoDB restore:

```powershell
docker-compose exec mongodb mongorestore --db stock_assistant /backup/stock_assistant
```

Redis backup (save snapshot):

```powershell
docker-compose exec redis redis-cli -a redispassword SAVE
```

Redis restore (copy snapshot):

```powershell
# Copy dump.rdb into redis container data directory
docker cp dump.rdb <redis_container_name>:/data/dump.rdb
```

Next steps

1. Start the application:

  ```powershell
  python src/main.py
  ```

1. Add test data via the application or API and confirm it persists after restart.

1. Optionally use MongoDB Compass or Redis monitoring tools for inspection and performance checks.

This completes the DB setup and migration documentation for local development and Docker-based environments.

## License

MIT


TBD - make the commit to note summary of previous PR change
