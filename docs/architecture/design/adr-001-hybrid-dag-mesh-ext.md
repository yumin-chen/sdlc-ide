---
title: "ADR-001: Hybrid Directed Graph Architecture"
status: Accepted
date: 2025-11-27
project: SDLC_IDE
author: System Architecture Team
---

# 1. Context
The SDLC_IDE platform requires a multi-agent architecture to manage SDLC artifacts. The system must enforce a verifiable core SDLC lifecycle while also supporting user-defined custom workflows and a safe, governed environment for extensibility.

**Key Requirements:**
- Deterministic and auditable lifecycle transitions.
- Support for both a default canonical pipeline and user-defined custom workflows.
- A clear separation between the authoritative SDLC lifecycle and flexible, semantic extensions.
- Central governance via an Orchestrator and Governor (OPA/Rego).

# 2. Decision
SDLC_IDE adopts a **Hybrid Directed Graph Architecture** with three integrated layers:
- **Core Strict Directed Acyclic Graph (DAG):** The authoritative, user-configurable SDLC lifecycle.
- **Selective Mesh Layer:** Flexible semantic documents and relations outside the Core lifecycle.
- **Event-Based Observer Layer:** An immutable event stream for analytics and observability.

# 3. Core DAG (Authoritative, Acyclic, User‑Configurable)
The Core DAG defines the authoritative SDLC lifecycle. Its sole invariant is **acyclicity**. While a default `PRD → TSD → ADR → KB` pipeline is provided, teams can register custom pipelines, which are validated by the Orchestrator. (See Appendix A).

# 4. Selective Mesh Layer (Extensions)
The Mesh Layer supports custom document types, semantic relations, and lateral workflows. All extensions must declare their schema and are validated by the Orchestrator and Governor.

# 5. Event-Based Observer Layer
An immutable, append-only event stream (per ADR-002) that provides full system observability without being authoritative for state. This maintains a strict separation between **structure** (graph) and **behavior** (events).

# 6. Rationale
The hybrid model is the only one that supports both **formal lifecycle guarantees** and **flexible extensibility**. It provides a stable, auditable foundation (the DAG) while allowing for rich, domain-specific extensions (the Mesh).

# 7. Decision Outcome
**Accepted.** This ADR establishes the foundational architecture of SDLC_IDE.

---

## Appendix A — Custom Workflow Registration & Enforcement
- **Summary:** Teams may register custom SDLC workflows via a declarative registry. The system-provided default pipeline is `PRD → TSD → ADR → KB`.
- **Validation:** The Orchestrator validates all workflows (acyclicity, type safety, ACLs) before activation.
- **Governance:** Workflow changes are PR-based and governed by OPA policy.
