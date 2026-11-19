# AGENTS.md: dp-stock-investment-assistant

An AI stock investment assistant: a Flask API with SSE streaming, a React + TypeScript SPA on Vite and Vitest,
a LangChain/LangGraph agent with MongoDB short-term memory, and MongoDB/Redis persistence.
Models are multi-provider, from OpenAI with fallbacks via `ModelClientFactory`.
Layering is **routes → services → repositories → DB**, with dependencies wired through service and repository factories.

## Project ownership
- **Product Owner for this project scope: Phan Duy.** Long-lived product docs name the Product Owner role; this file is the bot rulebook and names Phan explicitly as that Product Owner.

## Safety rules (read first)
- **Never edit the main working tree.** It holds many uncommitted changes. Make every edit in a named git worktree.
- **No commits, pushes, PRs or branch deletions without Phan's explicit approval** given for that action.
- **Never touch `main`/`master`.** Work only on the branch Phan assigns for the task; if none is named, ask before writing.
- Don't stage unrelated changes. In particular, leave the existing `.github/prompts` deletions out unless Phan asks for them.
- Keep secrets out of code, logs and output. `.env` is local only; use `.env.example` for keys.
- Before committing, run the relevant tests and `git diff --check`.

## Repo map
| Path | Contents |
|---|---|
| `src/` | Backend: Flask app (`src/main.py`), services, agent, `src/data/` (repositories, schema, migration), `src/utils/config_loader.py` |
| `frontend/` | React + TypeScript SPA on Vite and Vitest. Module folders are `features/` and `platform/`. |
| `tests/` | pytest suite |
| `config/` | `config.yaml` plus `config.{APP_ENV}.yaml` overlays |
| `IaC/` | Docker, Kubernetes/Helm, Terraform, CI/CD |
| `docs/` | Long-lived requirements, architecture, ADRs, technical design and policy |
| `specs/` | Delivery-scoped Spec Kit feature artifacts (`spec.md`, `plan.md`, `tasks.md`), plus `specs/spec-traceability.yaml` (traceability manifest; its `pitch-trace` block is script-generated) |
| `.specify/` | Spec Kit runtime: templates, extensions, scripts, and `memory/constitution.md` |
| `.github/instructions/` | Scoped coding rules (see below) |
| `.agents/skills/` | Agent skills (see below) |

## Frontend target stack

Sessions that touch `frontend/` follow the same rules as `frontend/AGENTS.md` and `.github/instructions/frontend-react.instructions.md`. Governing sections: `docs/domains/frontend/TECHNICAL_DESIGN.md` — "3.1 Module tree (Target M-000)" and "3.3 Boundary enforcement (Target G2)".

- Vite and Vitest.
- `VITE_*` environment variables only.
- No `socket.io-client`, WebSocket, or EventSource.
- `fetch` only inside `platform/api` and `platform/stream`.
- Module folders are `features/` and `platform/`. The shell is `app/` and shared UI is `design-system/`.
- Lint rules 1–3, as B1 enables them: dependency direction `app` → `features` → `platform` / `design-system`; no sibling-feature or deep imports; only `platform` talks to the Backend.

Do not recommend Create React App, Jest, `REACT_APP_*`, or Socket.IO.

## Setup & commands (Windows / PowerShell)
```powershell
python -m venv venv; venv\Scripts\Activate.ps1; pip install -r requirements.txt   # Python 3.10+
docker-compose up -d mongodb redis          # Windows may need docker-compose.override.yml (27034:27017)
python src\data\migration\db_setup.py       # schema, collections, indexes
python src\main.py --mode web               # API on :5000
cd frontend; npm install; npm run dev          # Vite UI
```
**Backend tests**
```powershell
$env:PYTHONPATH = "$PWD\src"
pytest -v                                     # all tests
pytest tests/test_agent.py -v; pytest -k "test_health" -v
pytest -m "not performance and not slow"      # fast loop (markers in pytest.ini)
pytest tests/ --cov=src --cov-fail-under=56 -q  # coverage non-regression gate (NFR-6.1.3)
```
**Frontend:** Vite and Vitest (`npx vitest run`, `npm run build`). Environment variables are `VITE_*` only. `fetch` stays inside `platform/api` and `platform/stream`.
**Spec traceability gate:** `python scripts/sync_spec_status.py --gate` (CI runs the same check in `.github/workflows/spec-trace.yml` and fails if regenerated files differ from the commit).
**Python lint/format:** none is configured. Follow PEP 8 and don't add tools without asking.

## Coding conventions (distilled; the scoped files are the authority)
- Use absolute imports from the `src` root, ordered stdlib → third-party → local. Avoid circular imports.
- Give public APIs and contracts type hints or TS interfaces. Comments explain *why*.
- Extend rather than mutate: add new modules and register them in factories. Prefer composition, except for the established bases `BaseService`, `MongoGenericRepository` and `CacheBackend`.
- All data access goes through `src/data/repositories/`. Use `db.command("listCollections")`, not `list_collection_names()`.
- Config load order: base YAML → `config.{APP_ENV}.yaml` → env vars → Key Vault. Respect `CONFIG_ENV_OVERRIDE_MODE`.
- The API returns JSON with standard status codes. Use one blueprint per domain. SSE uses `Response` + `stream_with_context`.
- Use structured logging, never `print`. Don't fail silently. Degrade gracefully, for example with model fallbacks.
- Tests mock the network, LLMs and DBs. Test behaviour, not implementation. A change isn't done until the tests are green.

## Scoped instructions: read the matching file before editing
| File (`.github/instructions/`) | Applies to |
|---|---|
| `architecture.instructions.md` | `**` |
| `backend-python.instructions.md`, `langchain-python.instructions.md` | `**/*.py` |
| `frontend-react.instructions.md` | `frontend/**` |
| `testing.instructions.md` | `tests/**` |
| `infrastructure-deployment.instructions.md` | `IaC/**` |
| `documentation-and-specification.instructions.md` | `docs/**`, `specs/**`, instruction files |

Repo-wide fallback: `.github/copilot-instructions.md`.

## Skills (`.agents/skills/<name>/SKILL.md`): load on demand, don't copy
- `research-to-architecture-adr`: architecture options, ADRs, ADR index, consistency reviews.
- `technical-design-manager`: keeps domain `TECHNICAL_DESIGN.md` in sync with specs and code.
- `commit-message-storyteller`: commit messages that explain *why*.
- `speckit-*`: the Spec Kit lifecycle (specify, clarify, plan, tasks, analyze, implement, verify-run, verify-tasks, doc-sync-gate) plus the architecture-guard, security-review, companion and harness extensions.
- Don't use `speckit-git-commit`, `speckit-git-initialize` or `speckit-taskstoissues` without Phan's approval, because they commit or create issues.

## Spec-Driven Development (Spec Kit)
1. Follow the flow `specify → clarify → plan → tasks → analyze → implement → verify`. Artifacts go in `specs/<feature>/`, governed by `.specify/memory/constitution.md`.
2. After spec→plan and plan→tasks, run the quality-gate cycle: consistency check → fix by severity → verify → sync long-lived docs.
3. Promote content to `docs/` only after the implementation is verified. Update the smallest owning doc and `specs/spec-traceability.yaml` together.
4. Traceability is ID-based and the child names its parent. A roadmap spec's `spec.md` front matter lists `pitch`, `slices`, `rows` and `deferred_rows` (convention in `specs/pitches/README.md`, "Traceability IDs"). Tag tasks with the row IDs they deliver, and put row IDs in test names. Never hand-edit reverse links.
5. Run the doc-sync gate (`speckit.doc-sync.gate`) after plan, implement and verify. It regenerates `specs/spec-sync-status.md`, the agent and system SRS reverse reports (`docs/domains/agent/SRS_SPEC_TRACEABILITY.md`, `docs/system/SRS_SPEC_TRACEABILITY.md`) and the `pitch-trace` block. It fails on a must-have row with no spec, a link to a nonexistent row ID, or a spec Status that differs from the derived status. Rows moved to a later Milestone are deferred, not orphans. The same run lists which spec delivers each pitch slice (`slice_delivery`, and the "Pitch delivery" table in `specs/spec-sync-status.md`). An unclaimed slice is a warning, and a claim on a slice the pitch doesn't have fails the gate. Commit the regenerated files with the change.
6. Each spec is registered under `features:` by the Traceability Manager. Set `srs_mapping.srs` to `system` or `agent`, with `baseline_version` equal to that SRS's version in `srs_documents`. An unmapped spec is excluded from the gate until it is mapped.
7. Keep sessions compact between phases. Full method: `docs/spec-driven development (SDD)/spec-kit HOW-TO.md`.

## Docs map (authority order: product/system → architecture → ADRs → domain design)
- Product: `docs/system/PRODUCT_SPECIFICATION.md`, `CONCEPTUAL_IA_MAP.md`, `USER_JOURNEYS_WITH_WIREFRAMES.md`, `SYSTEM_REQUIREMENTS_SPECIFICATION.md`, `REQUIREMENTS_METHOD_AND_GOVERNANCE.md`
- Naming: "Product" means the Product Definition and Specification (`docs/system/PRODUCT_SPECIFICATION.md`), whose roadmap defines Milestones `M-nnn`. "Spec" or "spec" means only a spec-kit `spec.md`.
- Architecture: `docs/architecture/SYSTEM_OVERVIEW_AND_BOUNDARIES.md`, `RUNTIME_AND_INTEGRATION_FLOWS.md`
- ADRs, in `docs/architecture/DECISIONS/`:
  - ADR-SYS-001 Identity & per-user isolation (Accepted in part)
  - ADR-SYS-002 Decision gate (Proposed)
  - ADR-SYS-003 Backend modular monolith (Proposed)
  - ADR-SYS-004 Data pipeline & records (Accepted)
  - ADR-SYS-005 External AI agent access (Proposed)
- Domain design: `docs/domains/{agent,backend,data,frontend}/TECHNICAL_DESIGN.md`, plus the agent SRS
- Operations/testing: `docs/operations/OPERATIONS_AND_RELEASE_POLICY.md`, `docs/testing/VERIFICATION_AND_TRACEABILITY_STRATEGY.md`
- Treat research, proposals and benchmarks (`docs/research/`, `docs/study-hub/`, `*_PROPOSAL*`) as non-authoritative input.


