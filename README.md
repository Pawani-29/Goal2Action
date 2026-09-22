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

## Domain models

`app/models/` contains dependency-free Python domain contracts. They use standard-library dataclasses, enums, and validation only; they do not depend on Microsoft Foundry, a database, APIs, RAG, or external services.

- `Goal` represents a user outcome and its target, constraints, success criteria, priority, and version.
- `Plan` is a versioned planning snapshot for one goal. A successor records its predecessor, preserving re-planning history.
- `Task` is an ordered work item linked to one goal and the plan revision that schedules it; parent and dependency IDs express task structure.
- `ProgressEvent` is a frozen, append-only execution record. It captures observed effort, status transitions, blockers, and evidence references.
- `Evidence` references material that supports a progress claim, with an explicit verification state.
- `UserContext` holds the V1 planning inputs: timezone, availability windows, and workload limits.
- `RiskAssessment` records a point-in-time comparison between remaining work and available capacity.

The relationship is `Goal -> Plan -> Task`, with `Goal/Task -> ProgressEvent -> Evidence`. `UserContext` supplies the user constraints used for planning, and `RiskAssessment` supplies a separate feasibility signal. New plans can supersede older plans while completed work remains represented in immutable progress events.
