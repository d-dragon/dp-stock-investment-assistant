# 📈 DP Stock-Investment Assistant — README (Developer Portal)

> **AI-Powered Financial Intelligence Platform & Trading Workspace for Retail Investors & Traders**  
> Combining multi-model LLM orchestration, automated market data ingestion & refinement, persistent decision memory, modern React visual workspace, and Spec-Driven Architecture.

---

## 📑 Table of Contents

- [1. Project Vision & Core Capabilities](#1-project-vision--core-capabilities)
  - [1.1 Product Overview & Value Proposition](#11-product-overview--value-proposition)
  - [1.2 Conceptual Model & Workspace Anatomy](#12-conceptual-model--workspace-anatomy)
  - [1.3 Key Capabilities by Domain](#13-key-capabilities-by-domain)
- [2. System Architecture & Topology](#2-system-architecture--topology)
  - [2.1 High-Level C4 Container Topology](#21-high-level-c4-container-topology)
  - [2.2 Governed Architecture References](#22-governed-architecture-references)
- [3. Development Environment Setup & Quick Start](#3-development-environment-setup--quick-start)
  - [3.1 Prerequisites & System Tooling](#31-prerequisites--system-tooling)
  - [3.2 Common Configuration & Secrets](#32-common-configuration--secrets)
  - [3.3 Domain-Based Quickstart Guides](#33-domain-based-quickstart-guides)
    - [Backend API & Persistence](#backend-api--persistence)
    - [AI Agent & LLM Models Integration](#ai-agent--llm-models-integration)
    - [Frontend & UX/UI](#frontend--uxui)
    - [Testing, QA & Traceability](#testing-qa--traceability)
    - [Infrastructure, Deployment & IaC](#infrastructure-deployment--iac)
- [4. Development Methodology & Documentation Hub](#4-development-methodology--documentation-hub)
  - [4.1 Spec-Driven Development (SDD) Lifecycle](#41-spec-driven-development-sdd-lifecycle)
  - [4.2 4-Directory Governance Matrix & Standards](#42-4-directory-governance-matrix--standards)
  - [4.3 Requirements-to-Delivery Traceability & Upward Promotion](#43-requirements-to-delivery-traceability--upward-promotion)
  - [4.4 Master Navigation & Document Directory](#44-master-navigation--document-directory)
- [5. Testing & Quality Assurance](#5-testing--quality-assurance)
- [6. Project Development Status & Strategic Roadmap](#6-project-development-status--strategic-roadmap)
  - [6.1 Delivered Capabilities by Domain](#61-delivered-capabilities-by-domain)
  - [6.2 Strategic Roadmap](#62-strategic-roadmap)
- [7. License & Contribution Guidelines](#7-license--contribution-guidelines)

---

## 1. Project Vision & Core Capabilities

> 📘 **Quick Navigation to Authoritative Documents**:  
> • **Product SSOT**: [`docs/system/PRODUCT_SPECIFICATION.md`](docs/system/PRODUCT_SPECIFICATION.md) — Product model, domain contracts, and roadmap.  
> • **Conceptual IA Map**: [`docs/system/CONCEPTUAL_IA_MAP.md`](docs/system/CONCEPTUAL_IA_MAP.md) — Information architecture and workspace zones.  
> • **User Journeys with Wireframes**: [`docs/system/USER_JOURNEYS_WITH_WIREFRAMES.md`](docs/system/USER_JOURNEYS_WITH_WIREFRAMES.md) — Techno-Fundamental user journey Pass→Position / Fail→Working Thesis + optional Case binder; proof frames W1–W6.  
> • **Vision & Capabilities Charter**: [`docs/system/PRODUCT_CAPABILITIES[Reserved].md`](docs/system/PRODUCT_CAPABILITIES%5BReserved%5D.md) — Market microstructure & 360° deep-dive.  

### 1.1 Product Overview & Value Proposition

The **DP Stock-Investment Assistant** is an intelligent, visual workspace engineered as a **Cognitive AI-powered Investment Workspace** for retail investors and active stock traders. Its primary journey owner is the **Techno-Fundamental Investor (TFI)**, who combines long-term business quality and valuation conviction with tactical technical execution, volume profiling, and strict risk discipline.

Modern stock investing subjects retail participants to four systemic handicaps:
1. **Information Asymmetry**: Fragmented, low-signal disclosures, delayed news, and unverified forum sentiment.
2. **Cognitive Overload**: Context shattered across dozens of disconnected tabs, charts, screeners, and note-taking apps.
3. **Single-Lens Myopia**: Flawed decisions caused by relying solely on technical chart patterns without balance-sheet checks, or vice-versa.
4. **Emotional & Process Drift**: Lack of recorded reasoning, causing thesis drift, disposition effect, panic selling, and unlearned mistakes.

**DP Stock solves this** by pairing an enabling **Platform** (Adaptive Workspace, AI Agents with Longitudinal Memory, and Data Hub with provenance) with a disciplined **Investment Core** (Insights, Living Thesis, Decision Gate, Portfolio, and Monitoring). It treats investing as a continuous, compounding lifecycle:

```text
Insights ──▶ Living Thesis ──▶ Decision Gate ──▶ Portfolio ──▶ Monitoring ──▶ Journal
   ▲                                                                             │
   └──────────────────────── (Intelligence Loop & Memory) ───────────────────────┘
```

---

### 1.2 Conceptual Model & Workspace Anatomy

DP Stock models investing as a **disciplined, continuous practice** rather than isolated transactions. The product is organized into two cooperating layers:

```mermaid
flowchart LR
    subgraph Platform["1. PLATFORM (Enabler)"]
        direction TB
        DATA["📊 Data Hub<br/>(VN-First & Provenance)"]
        CANVAS["🖥️ Visual Canvas<br/>(Adaptive Workspace)"]
        AI["🤖 AI Copilot<br/>(Long-Term Memory)"]
    end

    subgraph Core["2. INVESTMENT CORE (Reasoning)"]
        direction TB
        INS["Insights (360° Due Diligence)"]
        TH["Living Thesis (Bull vs. Bear)"]
        GATE{"Decision Gate (Pre-Mortem)"}
        PF["Portfolio (Execution & Sizing)"]
        MON["Monitoring (Thesis Drift)"]
        INS --> TH --> GATE -->|promote| PF --> MON
    end

    Platform ==>|powers & preserves context| Core
    MON -.->|learning loop| INS
```

> **Platform Principle — "Platform Enables, Core Means"**:  
> The Platform provides spatial tools, data ingestion, and AI reasoning, but **never owns investment meaning**. Final theses, risk decisions, and journal reflections are strictly user-owned.

#### Core Product Pillars

1. **Dual-Track Workflow (Sandbox vs. Portfolio)**:
   - **Research Sandbox (Track A)**: Freely explore ideas, inspect charts, and draft theses without altering real portfolio risk.
   - **Execution Portfolio (Track B)**: Governs live holdings, risk budgeting, and real capital allocations.
   - **The Decision Gate**: Ideas only promote to the portfolio by passing an explicit pre-mortem checklist (clear invalidation criteria, risk budget, and stop rules).
2. **Living Thesis with Multi-Stance**: Theses are living records tracking parallel **Bull and Bear** arguments, continuously monitored against earnings releases and news to prevent hindsight bias.
3. **Position at Pass + optional Case binder**: Decision **Pass** creates a **Position** (size, stop, official book). Fail/Revise never creates a Position — work stays a **Working Thesis**. An **Investment Case** is an **optional narrative binder / dossier thread** (anytime; not born at Pass; not the Position; not required).

#### The Unified Workspace Layout

All work takes place in a single, focused screen modeled after a professional workshop:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ Z2 · TOP CHROME (context)                                           [search · notif · acct] │
│ [VNM]  •  [Position after Pass]  •  [Case if linked]                                        │
├───────────────┬──────────────────────────────────────────────────┬──────────────────────────┤
│ Z1 · SIDEBAR  │ Z3 · MAIN WORKSPACE (wide)                       │ Z4 · AI COMPANION        │
│ DUAL-TRACK    │ • Active work and decision gate                  │ • Context-aware          │
│   A Research  │ • 360° forensic analysis & financials            │   co-analyst             │
│   B Portfolio │ • Living Thesis: parallel Bull / Bear            │ • Summarizes filings     │
│ LIFECYCLE     │ • Decision Gate: pre-mortem checklist            │   and news               │
│   Insights    │ • Price & volume market anchor (Sandbox)         │ • Challenges assumptions │
│   Thesis      │                                                  │ • Helps; never acts      │
│   Decision    │                                                  │   without investor       │
│   Portfolio   │                                                  │   confirmation           │
└───────────────┴──────────────────────────────────────────────────┴──────────────────────────┘
```

> For deep architectural specifications and wireframes, see [`CONCEPTUAL_IA_MAP.md`](docs/system/CONCEPTUAL_IA_MAP.md) and [`USER_JOURNEYS_WITH_WIREFRAMES.md`](docs/system/USER_JOURNEYS_WITH_WIREFRAMES.md).

---

### 1.3 Key Capabilities by Domain

| Layer | Domain / Capability | Description & Investor Benefit |
|---|---|---|
| **Platform** | **Knowledge Hub (Data & Information)** | Vietnam-first coverage (HOSE, HNX, UPCoM), financial footnotes (*Thuyết minh BCTC*), foreign/proprietary order flow, and news—all with strict source provenance tracking. |
| **Platform** | **Adaptive Visual Canvas (UX/UI)** | Multi-pane workspace with docked market chart anchors, context preservation across symbol switches, and saved layout presets. |
| **Platform** | **Cognitive AI & Memory** | Supporting companion (Z4), event briefings, thesis drift monitoring, and longitudinal memory profiling that learns the investor’s personal process. |
| **Core** | **Insights & 360° Synthesis** | Evidence-backed research synthesizing micro company fundamentals (forensics, moats), meso industry dynamics, and macro market drivers. |
| **Core** | **Living Thesis & Principles** | Version-controlled thesis builder featuring parallel Bull/Bear stances, explicit assumptions, and standing investment principles. |
| **Core** | **Decision Gate & Journal** | Pre-mortem checklist, position sizing guardrails, post-trade journaling, and cognitive bias detection (e.g. disposition effect). |
| **Core** | **Portfolio & Continuous Monitoring** | Position allocation, official risk tracking, automated thesis invalidation radars, and catalyst event tracking. |

## 2. System Architecture & Topology

### 2.1 High-Level C4 Container Topology

The system operates as a cohesive 3-container topology with clear boundary separation between presentation, API routing, agent intelligence, and persistence layers:

```mermaid
flowchart TB
    subgraph Clients["Presentation Tier"]
        FE["Frontend SPA\n(React + TypeScript + Nginx)\nPort: 3000"]
    end

    subgraph BackendTier["Application & API Tier"]
        API["Flask API Server\n(Gunicorn / Eventlet)\nPort: 5000"]
        AGENT["StockAssistantAgent\n(Prompt Compiler + Tool Gateway)\nPort: 7000"]
    end

    subgraph DataTier["Persistence & Cache Tier"]
        MONGO[("MongoDB 5.0+\n(Schemas, Workspaces, Sessions)\nPort: 27017")]
        REDIS[("Redis 6.0+\n(Cache Backend & STM)\nPort: 6379")]
    end

    subgraph ExternalServices["External Providers"]
        LLM["Multi-Model LLMs\n(OpenAI GPT-4, xAI Grok)"]
        MKT["Financial Data Feeds\n(Vietnam & Global Market Feeds)"]
    end

    FE <-->|REST API / SSE Streaming / Socket.IO| API
    API <-->|Service Layer & Context DI| AGENT
    AGENT <-->|ModelClientFactory / Fallback| LLM
    AGENT <-->|Tool Gateway & Normalization| MKT
    API <-->|Repository Factory| MONGO
    API <-->|CacheBackend| REDIS
    AGENT <-->|STM & Session Persistence| MONGO
    AGENT <-->|Prompt & Tool Caching| REDIS
```

### 2.2 Governed Architecture References

For detailed structural specifications, component designs, and deployment models, consult the authoritative architecture documentation:

- 🏛️ **[System Overview & Boundaries](docs/architecture/SYSTEM_OVERVIEW_AND_BOUNDARIES.md)** — arc42 §3, §4, §5 Level 1 system building blocks and container scopes.
- 🔄 **[Runtime & Integration Flows](docs/architecture/RUNTIME_AND_INTEGRATION_FLOWS.md)** — arc42 §6 dynamic sequence flows, streaming chat, and tool execution lifecycles.
- ☁️ **[Deployment & Cloud Infrastructure](docs/architecture/DEPLOYMENT_AND_INFRASTRUCTURE.md)** — arc42 §7 Docker, Kubernetes/Helm, and Azure AKS/ACR infrastructure.
- 🧠 **[Agent Domain Architecture](docs/domains/agent/ARCHITECTURE_DESIGN.md)** — Deep-dive agent reasoning graph, prompt compiler, and tool gateway design.

---

## 3. Development Environment Setup & Quick Start

### 3.1 Prerequisites & System Tooling

Ensure the following tools and runtimes are installed on your workstation based on your development and operational focus:

| Category | Tool / Runtime | Minimum Version | Purpose |
|---|---|---|---|
| **Backend/Frontend Runtimes** | **Python** | `3.10+` (or `3.8+`) | Core Flask API, AI agent reasoning, and data migrations |
| | **Node.js & npm** | `v18.0+` (LTS) / `npm 9.0+` | React frontend single-page application and UI build |
| **AI Frameworks & Tooling** | **LangChain & LangGraph** | `0.1.0+` / `0.0.20+` | Multi-agent state graph orchestration, tool gateway integration, and workflow loops |
| | **LangSmith CLI & Studio** | `langgraph-cli[inmem]` | Real-time agent execution trace analysis, prompt debugging, and visual graph inspection |
| **Data & Persistence** | **MongoDB** | `5.0+` (or via Docker) | Document persistence for users, sessions, workspaces, and market data |
| | **Redis** | `6.0+` (or via Docker) | High-speed cache, rate-limiting, and Short-Term Memory (STM) buffer |
| **Infrastructure & IaC** | **Docker & Docker Compose** | `20.10+` / Compose `v2+` | 3-container orchestration (`api`, `agent`, `frontend`) and local databases |
| | **Kubectl** | `1.26+` | Local and cloud Kubernetes cluster management and pod inspection |
| | **Helm** | `v3.10+` | Packaging, templating, and deploying Kubernetes charts (`IaC/helm/dp-stock`) |
| | **Terraform** | `v1.5+` | Azure Cloud infrastructure provisioning (Resource Group, ACR, AKS) |
| | **Azure CLI (`az`)** | `2.45+` | Azure cloud authentication, ACR pull credentials, and AKS cluster access |
| **Testing & Quality** | **pytest & pytest-cov** | `7.0+` / `4.0+` | Backend unit, integration, and service-layer test suite with coverage reports |
| | **Jest & RTL** | `29.0+` / `14.0+` | Frontend component testing, hook isolation, and DOM assertions |
| **Version Control & CI/CD** | **Git** | `2.30+` | Version control, branch policies, and Spec Kit metadata tracking |
| | **GitHub Actions** | `v2+` | Automated CI/CD workflows, build pipelines, and gate verification |

> [!TIP]
> **Windows Port Reservation Notice**: On Windows hosts, port `27017` is occasionally reserved by Hyper-V / NAT services. If MongoDB fails to bind, map host port `27034` to container `27017` using `docker-compose.override.yml` and update `MONGODB_URI` accordingly.

### 3.2 Common Configuration & Secrets

The repository loads configuration through a hierarchical cascade: `config/config.yaml` ➔ `config/config.{APP_ENV}.yaml` ➔ `.env` / Environment Variables ➔ Azure Key Vault.

1. **Initialize configuration files**:
   ```powershell
   # Windows PowerShell
   Copy-Item .env.example .env
   Copy-Item config\config_example.yaml config\config.yaml
   ```

2. **Configure critical environment variables in `.env`**:
   ```dotenv
   # AI Model Providers
   OPENAI_API_KEY=your-openai-api-key-here
   GROK_API_KEY=your-grok-api-key-here
   MODEL_PROVIDER=openai

   # Persistence & Cache
   MONGODB_URI=mongodb://stockadmin:stockpassword@localhost:27017/stock_assistant?authSource=stock_assistant
   MONGODB_DB_NAME=stock_assistant
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=redispassword

   # Application Environment
   APP_ENV=local
   APP_LOG_LEVEL=INFO
   ```

---

### 3.3 Domain-Based Quickstart Guides

#### Backend API & Persistence

```powershell
# 1. Setup Python Virtual Environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# 2. Start Local MongoDB & Redis Containers
docker-compose up -d mongodb redis

# 3. Run Database Migrations & Create Schema Indexes
python src\data\migration\db_setup.py

# 4. Start Flask Development API Server (Port 5000)
python src\main.py --mode web

# 5. Smoke-Test Backend Health
curl http://localhost:5000/api/health
```

📖 *For comprehensive PowerShell scripts, WSGI server configs, and curl smoke tests, see **[`QUICK_START.md`](QUICK_START.md)** and **[`docs/domains/backend/TECHNICAL_DESIGN.md`](docs/domains/backend/TECHNICAL_DESIGN.md)**.*

---

#### AI Agent & LLM Models Integration

```powershell
# 1. Interactive Agent CLI Mode (Direct Terminal Chat)
python src\main.py --mode cli

# 2. Visual Reasoning Graph Debugging (LangSmith Studio)
pip install "langgraph-cli[inmem]"
$env:LANGSMITH_API_KEY = "lsv2_..."
langgraph dev
# Open Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

# 3. Python REPL Streaming Test Snippet
python -c "
from core.agent import StockAgent
from core.data_manager import DataManager
from utils.config_loader import ConfigLoader
cfg = ConfigLoader.load_config()
agent = StockAgent(cfg, DataManager(cfg))
for chunk in agent.process_query_streaming('Analyze VNM stock technicals'):
    print(chunk, end='', flush=True)
"
```

📖 *For prompt compiler mechanics, tool gateway descriptors, and model fallback policies, see **[`docs/domains/agent/ARCHITECTURE_DESIGN.md`](docs/domains/agent/ARCHITECTURE_DESIGN.md)** and **[`docs/domains/agent/LANGCHAIN_AGENT_HOWTO.md`](docs/domains/agent/LANGCHAIN_AGENT_HOWTO.md)**.*

---

#### Frontend & UX/UI

```powershell
# 1. Navigate to Frontend Directory
cd frontend

# 2. Install Node Dependencies
npm install

# 3. Start React Development Server (Port 3000)
npm start
```

The browser will automatically open `http://localhost:3000`. The frontend will connect to `http://localhost:5000` for REST API and Socket.IO real-time streaming.

🎨 **Figma UX/UI reference**: [Open the UX/UI design in Figma](https://www.figma.com/design/Jy1qyQeJJT1gaQVar8KJLd/Stock-Investment-Assistant?m=dev&t=ri6ZCr5ojO5e0ErZ-1). 

The Figma page is a design reference for the frontend implementation; React components and live API behavior remain owned by `frontend/src/` and the backend contracts.

📖 *For component architecture, UI state management, and mock mode options, see **[`frontend/REACT_SETUP_GUIDE.md`](frontend/REACT_SETUP_GUIDE.md)**, **[`frontend/README.md`](frontend/README.md)**, and **[`docs/domains/frontend/ARCHITECTURE.md`](docs/domains/frontend/ARCHITECTURE.md)**.*

---

#### Testing, QA & Traceability

```powershell
# 1. Setup Test Environment Variables
$env:PYTHONPATH = "$PWD\src"

# 2. Run Complete Backend Test Suite
pytest -v

# 3. Run Targeted Domain Test Suites
pytest tests\test_api_routes.py tests\test_chat_routes.py tests\test_health_routes.py -v
pytest tests\test_tools.py tests\test_tool_gateway_m2b1.py tests\test_market_data_tools.py -v
pytest tests\test_agent_memory.py tests\test_session_service.py -v

# 4. Generate Backend Coverage Report
pytest --cov=src --cov-report=term-missing --cov-report=html

# 5. Run Frontend Component & Unit Tests
cd frontend
npm test -- --watchAll=false --coverage

# 6. Verify Spec Traceability Gate Compliance
cd ..
python scripts\sync_spec_status.py --gate
```

📖 *For comprehensive mocking patterns, test fixture catalogs, and performance/security benchmarks, see `docs/testing/`, **[`.github/instructions/testing.instructions.md`](.github/instructions/testing.instructions.md)**.*

---

#### Infrastructure, Deployment & IaC

```powershell
# 1. Local Full-Stack 3-Container Build & Launch
docker-compose up --build

# 2. Local Kubernetes Deployment with Helm
helm upgrade --install dp-stock IaC/helm/dp-stock `
  -n dp-stock --create-namespace `
  -f IaC/helm/dp-stock/values.local.yaml

# 3. Port-Forward Services for Validation
kubectl -n dp-stock port-forward svc/dp-stock-api 5000:5000
kubectl -n dp-stock port-forward svc/dp-stock-frontend 3000:80
```

📖 *For Terraform Azure AKS/ACR provisioning, Helm chart overrides, and production container guidelines, see **[`IaC/README.md`](IaC/README.md)** and **[`docs/architecture/DEPLOYMENT_AND_INFRASTRUCTURE.md`](docs/architecture/DEPLOYMENT_AND_INFRASTRUCTURE.md)**.*

---

## 4. Development Methodology & Documentation Hub

### 4.1 Spec-Driven Development (SDD) Lifecycle

This project follows **Spec-Driven Development (SDD)** with **Spec Kit**, ensuring that every feature begins with structured Markdown specifications, passes explicit quality gates, and generates verifiable evidence before code is merged:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ 1. Requirements │ ──> │ 2. Specification │ ──> │ 3. Planning     │ ──> │ 4. Implement    │ ──> │ 5. Promotion    │
│ & Governance    │     │ & Refinement     │     │ & Review        │     │ & Verification  │     │ & Sync Gate     │
└─────────────────┘     └──────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
  • System SRS            • speckit.specify        • speckit.plan          • speckit.implement     • sync_spec_status
  • Constitution          • speckit.clarify        • speckit.tasks         • verify-tasks.run      • arc42 promotion
                          • speckit.checklist      • fleet.review          • verify.run            • RTM update
```

### 4.2 4-Directory Governance Matrix & Standards

Documentation is structured across **4 authoritative directories** aligned with ISO/IEC/IEEE 42010, arc42, and C4 standards:

| Directory | Standard / Authority | Purpose & Lifecycle Role | Key Artifacts |
|---|---|---|---|
| **`docs/system/`** | ISO 29148 / ISO 25010 | Authoritative System Requirements Specification (SRS) baseline; cross-domain functional and quality requirements. | [System SRS](docs/system/SYSTEM_REQUIREMENTS_SPECIFICATION.md)<br>[Method & Governance](docs/system/REQUIREMENTS_METHOD_AND_GOVERNANCE.md) |
| **`docs/architecture/`** | arc42 / C4 Model / ISO 42010 | Long-lived system architecture views, deployment topology, cross-cutting mechanisms, risks, and ADRs. | [System Overview](docs/architecture/SYSTEM_OVERVIEW_AND_BOUNDARIES.md)<br>[Deployment & Infra](docs/architecture/DEPLOYMENT_AND_INFRASTRUCTURE.md)<br>[Cross-Cutting Concepts](docs/architecture/CROSS_CUTTING_CONCEPTS.md)<br>[Risks & Debt](docs/architecture/RISKS_AND_TECHNICAL_DEBT.md)<br>[ADRs](docs/architecture/DECISIONS/) |
| **`docs/domains/`** | Domain-Driven Design (DDD) | Bounded context technical designs, component internals (C4 Level 3), and subordinate domain SRS documents. | [Agent Architecture](docs/domains/agent/ARCHITECTURE_DESIGN.md)<br>[Backend Design](docs/domains/backend/TECHNICAL_DESIGN.md)<br>[Frontend Architecture](docs/domains/frontend/ARCHITECTURE.md)<br>[Data Policy](docs/domains/data/POLICY_AND_CONSTRAINTS.md) |
| **`specs/`** | Spec Kit Feature Deltas | Delivery-scoped feature specifications, implementation plans, user-story tasks, verification reports, and RTM manifest. | [Traceability Manifest](specs/spec-traceability.yaml)<br>[Forward Sync Report](specs/spec-sync-status.md)<br>[Feature Specs](specs/) |

### 4.3 Requirements-to-Delivery Traceability & Upward Promotion

The platform enforces a closed-loop engineering discipline connecting high-level system requirements to verified code and durable architecture views:

```
┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│ 1. Upstream SRS Pool   │ ───> │ 2. Feature Spec Deltas │ ───> │ 3. arc42 Promotion     │
│ docs/system/ & domains/│      │ specs/<feature-id>/    │      │ docs/architecture/     │
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘
          │                                  │                              ▲
          ▼                                  ▼                              │
┌────────────────────────────────────────────────────────┐                  │
│       Authoritative RTM (specs/spec-traceability.yaml) ├──────────────────┘
│          Automated Gates & Forward/Reverse Reports     │
└────────────────────────────────────────────────────────┘
```

#### Core Operational Disciplines:

1. **Upstream Requirement Sourcing**: Feature specifications in `specs/<feature-id>/spec.md` draw directly from system and domain SRS requirement IDs (e.g., `SR-x`, `SNR-x`, `FR-x`, `NFR-x`), establishing explicit provenance.
2. **Automated Traceability Manifest & Gates**: [`specs/spec-traceability.yaml`](specs/spec-traceability.yaml) tracks delivery gates (`clarified` ➔ `planned` ➔ `implemented` ➔ `verified`).
   ```powershell
   python scripts/sync_spec_status.py        # Regenerate forward/reverse sync reports
   python scripts/sync_spec_status.py --gate # Enforce CI/CD compliance gate
   ```
   - ➔ **[Forward Feature-to-SRS Report](specs/spec-sync-status.md)** | **[Reverse SRS Trace Report](docs/domains/agent/SRS_SPEC_TRACEABILITY.md)**
3. **Quality Gate Chain & Compaction**: Progress features through structured gates (`speckit.checklist` ➔ `speckit.fleet.review` ➔ `speckit.verify-tasks.run` ➔ `speckit.verify.run`), running `/compact` at major phase boundaries to keep AI agent context clean.
4. **arc42 Upward Knowledge Promotion**: Verified feature specs act as local delivery evidence. Stable architectural patterns are promoted upward into long-lived docs:
   - System Containers ➔ [`docs/architecture/SYSTEM_OVERVIEW_AND_BOUNDARIES.md`](docs/architecture/SYSTEM_OVERVIEW_AND_BOUNDARIES.md) (arc42 §3–§5)
   - Runtime Flows ➔ [`docs/architecture/RUNTIME_AND_INTEGRATION_FLOWS.md`](docs/architecture/RUNTIME_AND_INTEGRATION_FLOWS.md) (arc42 §6)
   - Infrastructure Topology ➔ [`docs/architecture/DEPLOYMENT_AND_INFRASTRUCTURE.md`](docs/architecture/DEPLOYMENT_AND_INFRASTRUCTURE.md) (arc42 §7)
   - Cross-Cutting Concepts ➔ [`docs/architecture/CROSS_CUTTING_CONCEPTS.md`](docs/architecture/CROSS_CUTTING_CONCEPTS.md) (arc42 §8)
   - Architectural Decisions ➔ [`docs/architecture/DECISIONS/`](docs/architecture/DECISIONS/) (arc42 §9 / ADRs)
   - API Contracts ➔ [`docs/openapi.yaml`](docs/openapi.yaml) (Golden Rule 9)

📖 *For the complete 18-step SDD lifecycle, CLI commands, persistence rules, and troubleshooting, see the authoritative guide: **[`docs/spec-driven development (SDD)/spec-kit HOW-TO.md`](docs/spec-driven%20development%20%28SDD%29/spec-kit%20HOW-TO.md)**.*

### 4.4 Master Navigation & Document Directory

- 📘 **[Project Documentation & Specification Methodology](docs/study-hub/project-documentation-and-specification-methodology.md)** — Tripartite architecture framework (ISO 42010, arc42, C4, ISO 25010) and document boundary rules.
- 🛠️ **[Spec Kit SDD HOW-TO Guide](docs/spec-driven%20development%20%28SDD%29/spec-kit%20HOW-TO.md)** — Comprehensive 18-step SDD execution manual, CLI flags, and troubleshooting.
- 📋 **[Public API OpenAPI 3.0 Contract](docs/openapi.yaml)** — Authoritative machine-readable REST API contract.
- 🛡️ **[Project Constitution & Quality Rules](.specify/memory/constitution.md)** — Non-negotiable architectural principles, memory boundaries, and golden rules.
- 🤖 **[AI Coding Agent Instructions](.github/copilot-instructions.md)** — Repository conventions, import rules, and domain guides in [`.github/instructions/`](.github/instructions/).

---

## 5. Testing & Quality Assurance

The project employs a multi-tiered testing and verification strategy designed for offline execution, protocol-based dependency injection, and complete isolation from external paid APIs during automated CI runs.

### 5.1 Test Levels & Architecture Scope

| Testing Level | Scope & Target Capabilities | Tooling & Frameworks | Key Test Paths / Guides |
|---|---|---|---|
| **Unit & Mock Testing** | Core business logic, prompt compilers, tool descriptors, and data utilities | `pytest`, `pytest-mock`, `unittest.mock` | `tests/unit/`, `tests/fixtures/` |
| **API & Contract Testing** | REST endpoints, SSE chat streaming, Socket.IO events, and schema compliance | `pytest`, `FlaskClient`, `schemathesis` | `tests/api/`, [API Tests Runbook](tests/API%20tests.md) |
| **Service & Repository Integration** | Layered DI wiring, MongoDB schema validation, and Redis cache failovers | `pytest`, in-memory stubs | `tests/integration/`, `tests/helpers/` |
| **AI Agent & Tool Verification** | Agent reasoning flow, symbol normalization, market tools, and STM memory | `pytest`, stubs, LangSmith traces | `tests/test_tools.py`, `tests/test_agent_memory.py` |
| **Frontend Component Testing** | React components, UI state hooks, streaming handlers, and DOM assertions | `Jest`, `React Testing Library` | `frontend/src/**/*.test.tsx` |
| **Performance & Security Testing** | Latency benchmarks, prompt injection defenses, and secret leakage audits | `pytest-benchmark`, pytest fixtures | `tests/performance/`, `tests/security/` |

### 5.2 Test Execution Runbook

```powershell
# Set Python path for module resolution
$env:PYTHONPATH = "$PWD\src"

# Run complete backend test suite
pytest -v

# Run targeted test suites
pytest tests/test_api_routes.py tests/test_chat_routes.py -v       # API & Chat Routes
pytest tests/test_tools.py tests/test_tool_gateway_m2b1.py -v     # Tool Gateway & Descriptors
pytest tests/test_agent_memory.py tests/test_session_service.py -v # Memory & Sessions

# Generate coverage report
pytest --cov=src --cov-report=term-missing --cov-report=html

# Run frontend tests
cd frontend; npm test -- --watchAll=false --coverage
```

### 5.3 Testing Documentation & Reference Links

- 📋 **[Testing Strategy & Tool Comparison](docs/testing/API_TEST_TOOL_COMPARISON_REPORT.md)** — Comprehensive evaluation of pytest, Newman, Bruno, and Schemathesis for API integration.
- 📘 **[Verification & Traceability Strategy](docs/testing/VERIFICATION_AND_TRACEABILITY_STRATEGY.md)** — Quality gates, phantom completion checks, and test-to-requirement coverage.
- 🛠️ **[Testing Conventions & Fixture Guide](.github/instructions/testing.instructions.md)** — Detailed guidelines for protocol mocking, cache fixtures, and async frontend testing.
- 🧪 **[API Testing Runbook](tests/API%20tests.md)** — Quick verification commands and test suite breakdowns.

---

## 6. Project Development Status & Strategic Roadmap

### 6.1 Delivered Capabilities by Domain

The platform's verified milestones and implemented capabilities are categorized by bounded context:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DELIVERED CAPABILITIES                                 │
├────────────────────────┬────────────────────────┬──────────────────────────────────────┤
│ Domain                 │ Capability / Milestone │ Status                               │
├────────────────────────┼────────────────────────┼──────────────────────────────────────┤
│ Agent Intelligence     │ Short-Term Memory (STM)│ [Verified] (specs/stm-phase-cde)     │
│ Agent Intelligence     │ Prompt Compiler M1/M2  │ [Implemented] (specs/prompt-system-m2)│
│ Agent Intelligence     │ Tool Gateway (M2B.1)   │ [Verified] (specs/tool-system-m2b.1) │
│ Agent Intelligence     │ Symbol Normalization   │ [Verified] (specs/tool-system-m2b.2) │
│ Agent Intelligence     │ Vietnam Market & Charts│ [Verified] (specs/tool-system-m2b.3) │
│ Agent Intelligence     │ Multi-Model & Fallback │ [Verified] (OpenAI + Grok)           │
│ Agent Intelligence     │ Structured Outputs     │ [Implemented] (specs/003-structured) │
│ Core API & Services    │ Blueprint Architecture │ [Verified] (src/web/routes)          │
│ Core API & Services    │ Service/Repo Factories │ [Verified] (src/services, src/data)  │
│ Core API & Services    │ MongoDB Migrations     │ [Verified] (src/data/migration)      │
│ Core API & Services    │ Redis Caching Backend  │ [Verified] (src/utils/cache.py)      │
│ Frontend Experience    │ React TypeScript SPA   │ [Verified] (frontend/src)            │
│ Frontend Experience    │ Real-Time SSE/Sockets  │ [Verified] (Chat & Streaming)        │
│ Frontend Experience    │ Model Switcher UI      │ [Verified] (Config & Model Selection)│
│ Infrastructure & IaC   │ Docker 3-Container Topo│ [Verified] (IaC/Dockerfile.*)        │
│ Infrastructure & IaC   │ Kubernetes Helm Chart  │ [Verified] (IaC/helm/dp-stock)       │
│ Infrastructure & IaC   │ Terraform AKS / ACR    │ [Verified] (IaC/infra/terraform)     │
└────────────────────────┴────────────────────────┴──────────────────────────────────────┘
```

### 6.2 Strategic Roadmap

```
                       ┌──────────────────────────────────────────────┐
                       │          STRATEGIC PROJECT ROADMAP           │
                       └──────────────────────────────────────────────┘
                                              │
    ┌───────────────────┬─────────────────────┼─────────────────────┬───────────────────┐
    ▼                   ▼                     ▼                     ▼                   ▼
┌───────────────┐ ┌───────────────┐   ┌───────────────┐     ┌───────────────┐   ┌───────────────┐
│ Milestone 3   │ │ Milestone 4   │   │ Milestone 5   │     │ Milestone 6   │   │ Milestone 7   │
│ Long-Term Mem │ │ Multi-Agent   │   │ Quantitative  │     │ Production    │   │ Mobile &      │
│ Vector RAG    │ │ LangGraph     │   │ Portfolio Opt │     │ AKS CI/CD     │   │ Notification  │
│ (Q3 2026)     │ │ (Q4 2026)     │   │ (Q1 2027)     │     │ (Q2 2027)     │   │ (Q3 2027)     │
└───────────────┘ └───────────────┘   └───────────────┘     └───────────────┘   └───────────────┘
```

- 🎯 **Milestone 3 (M3) — Long-Term Memory (LTM) Vector RAG**: Hybrid semantic search, Vector embeddings for market news & SEC filings, and Graph-based entity relationships.
- 🎯 **Milestone 4 (M4) — Autonomous Multi-Agent Collaboration**: LangGraph supervisor architecture with specialized subagents for Fundamental Analysis, Technical Analysis, and Risk Assessment.
- 🎯 **Milestone 5 (M5) — Quantitative Portfolio Optimization**: Portfolio backtesting engine, Black-Litterman allocation model, Monte Carlo risk simulation, and automated rebalancing alerts.
- 🎯 **Milestone 6 (M6) — Production Azure Cloud CI/CD**: Automated GitHub Actions pipeline for ACR image scanning, Helm deployments, automated canary rollouts, and Azure Key Vault secret injection.
- 🎯 **Milestone 7 (M7) — Multi-Channel Alerting & Mobile UI**: Push notifications, Telegram/Discord webhooks for trade alerts, and progressive mobile web experience.

---

## 7. License & Contribution Guidelines

### 7.1 License
[TBD]

### 7.2 Contribution & Engineering Standards
[TBD]

---

*This README as Developer Portal — Maintained by the Engineering Team.*
