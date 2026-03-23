# dp-stock-investment-assistant Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-23

## Active Technologies
- Python 3.8+ + Flask blueprints, Flask-SocketIO, PyMongo repositories, Redis-backed `CacheBackend`, LangGraph `MongoDBSaver`, pytest (stm-phase-cde)
- MongoDB 5.0 (`workspaces`, `sessions`, `conversations`, `agent_checkpoints`, supporting audit/report collections if added), Redis 6.2 cache (stm-phase-cde)

- Python 3.8+ (per Constitution Article VIII) + LangGraph >=0.2.0, LangChain >=1.0.0, Flask 2.x, PyMongo 4.x (spec-driven-development-pilot)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.8+ (per Constitution Article VIII): Follow standard conventions

## Recent Changes
- stm-phase-cde: Added Python 3.8+ + Flask blueprints, Flask-SocketIO, PyMongo repositories, Redis-backed `CacheBackend`, LangGraph `MongoDBSaver`, pytest

- spec-driven-development-pilot: Added Python 3.8+ (per Constitution Article VIII) + LangGraph >=0.2.0, LangChain >=1.0.0, Flask 2.x, PyMongo 4.x

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
