---
description: Architecture, system design, and infrastructure conventions for dp-stock-investment-assistant
applyTo: "**"
---

# Architecture and System Design

## Project Architecture Overview
- **Microservices Pattern**: API, Agent (background worker), and Frontend served independently
- **Tech Stack**: Python 3.8+ (Flask/FastAPI), React 18, MongoDB 5.0, Redis 6.2
- **Communication**: REST API + Socket.IO for real-time chat streaming
- **Deployment**: Docker Compose (local), Kubernetes/AKS (production via Helm)

## Directory Structure
- `src/` - Backend Python application
  - `core/` - Agent, model factory/clients, data manager
  - `web/` - Flask blueprints (routes/, sockets/) for API
  - `data/` - Repositories, schema, services, migrations
  - `utils/` - Config loader, model router, helpers
- `frontend/` - React TypeScript application
- `IaC/` - Infrastructure as Code
  - `Dockerfile.api`, `Dockerfile.agent` - Container images
  - `helm/dp-stock/` - Kubernetes Helm chart
  - `infra/terraform/` - Azure resource provisioning
- `config/` - YAML configuration files with environment overlays
- `.github/` - Copilot instructions, chat modes, model routing config

## Design Patterns
- **Immutable Configuration Context**: Use dataclasses (frozen=True) for dependency injection in Flask blueprints
- **Factory Pattern**: ModelFactory for creating provider-specific AI model clients
- **Repository Pattern**: Centralize database access in repositories; avoid ad-hoc DB calls in routes
- **Blueprint Architecture**: Modular Flask route organization (api_routes, models_routes)
- **Streaming Protocol**: SSE (Server-Sent Events) for chat response streaming with Flask Response + stream_with_context

## Infrastructure Conventions
- **Local Override Pattern**: Keep docker-compose.yml upstream-friendly; use docker-compose.override.yml for local tweaks (e.g., port mappings)
- **Multi-Environment Config**: Base `config.yaml` + environment overlays (`config.local.yaml`, `config.k8s-local.yaml`, `config.staging.yaml`, `config.production.yaml`)
- **Secret Management**: Use Azure Key Vault in production; environment variables for local/staging
- **Container Health Probes**:
  - API: `GET /api/health` on port 5000
  - Agent: `GET /health` on port 7000
  - Frontend: `GET /healthz` on port 80

## Deployment Architecture
- **Local Development**: docker-compose with hot-reload for API and frontend dev servers
- **Production (AKS)**:
  - API: gunicorn with eventlet/gevent worker for WebSocket support
  - Agent: Background worker with health endpoint
  - Frontend: Nginx serving static React build
  - Ingress routing: `/` → frontend, `/api` → API service

## Architectural Decisions
- **Why Socket.IO**: Real-time bidirectional communication for chat streaming; fallback to polling for network constraints
- **Why MongoDB Time-Series**: Efficient storage and querying of market data with automatic data expiration
- **Why Redis**: Session caching, rate limiting, and temporary storage for financial API responses
- **Why Helm**: Declarative Kubernetes deployments with environment-specific value overrides

## Infrastructure as Code Best Practices
- **Terraform**: Provision Azure resources (Resource Group, ACR, AKS) with managed identity and OIDC
- **Helm Chart Structure**:
  - `values.yaml` - Defaults (dev-friendly)
  - `values.production.yaml` - Production overrides (replicas, resources, ingress)
  - Templates: deployments, services, ingress, configmaps
- **Image Management**: Build in CI, push to ACR, deploy via Helm with image.tag overrides
- **Probe Alignment**: Ensure containerPort, health endpoints, and Helm probe paths match across all layers

## System Integration Points
- **Financial Data APIs**: Yahoo Finance (primary), Alpha Vantage (optional)
- **AI Model Providers**: OpenAI, xAI Grok with fallback support
- **Database Layer**: MongoDB for persistence, Redis for caching
- **WebSocket Events**: Centralized in `API_CONFIG.WEBSOCKET.EVENTS` for frontend/backend alignment

## Scalability Considerations
- API and Agent pods scale independently via Helm replica settings
- MongoDB uses connection pooling; avoid N+1 query patterns
- Redis TTL configuration per data type (price_data: 60s, fundamental_data: 24h)
- Frontend served as static assets; scales via CDN or Nginx replicas

## Security Architecture
- **Secret Storage**: Never commit secrets; use .env (local), Azure Key Vault (production)
- **API Authentication**: Prepare for token-based auth (placeholder for future OAuth/JWT)
- **CORS Configuration**: Restrict origins in production; configurable via environment variables
- **MongoDB Auth**: SCRAM-SHA-256 with least-privilege users per collection
- **Container Security**: Non-root users, minimal base images, vulnerability scanning in CI

## References
- IaC/K8s details: `IaC/README.md`
- Model routing: `.github/MODEL_ROUTING.md`, `.github/copilot-model-config.yaml`
- API specification: `docs/openapi.yaml`
