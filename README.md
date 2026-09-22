# Goal2Action

Goal2Action is an Agentic AI personal execution agent for students, planned to use Microsoft Foundry. This repository currently contains only a local architecture scaffold; it has no application implementation, dependencies, Azure resources, or external integrations.

## Project structure

- `app/` — Application composition and entry-point layer. It will connect modules without owning agent logic.
- `agent/` — Agent and orchestration responsibilities. This stays separate from callable tools and integrations.
- `knowledge/` — Knowledge and future RAG ingestion, indexing, and retrieval boundaries.
- `planning/` — Goal decomposition, scheduling, and execution-planning concerns, independent of knowledge retrieval.
- `tools/` — Tool contracts and isolated adapters the agent can invoke; no orchestration belongs here.
- `memory/` — User memory, session state, and persistence boundaries, separate from knowledge/RAG.
- `models/` — Shared domain models and data contracts.
- `services/` — External service integration boundaries and infrastructure-facing adapters.
- `tests/` — Tests mirroring module responsibilities as implementation is added.

## Configuration

`.env.example` is intentionally blank of service-specific settings for now. Add only non-secret configuration examples when those integrations are intentionally introduced.
