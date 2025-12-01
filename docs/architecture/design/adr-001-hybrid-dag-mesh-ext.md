---
title: "ADR-001: Hybrid Directed Graph Architecture"
status: Accepted
date: 2025-11-27
project: SDLC_IDE
author: System Architecture Team
---

# 1. Context
The SDLC_IDE platform requires a multi-agent architecture to manage SDLC artifacts. The system must enforce a verifiable core SDLC lifecycle while also supporting user-defined custom workflows and a safe, governed environment for extensibility.

# 2. Decision
SDLC_IDE adopts a **Hybrid Directed Graph Architecture** with three integrated layers:
- **Core Strict Directed Acyclic Graph (DAG):** The authoritative SDLC lifecycle.
- **Selective Mesh Layer:** Flexible semantic documents, extensions, and custom workflows.
- **Event-Based Observer Layer:** An immutable event stream for analytics and observability.

# 3. Core DAG (Authoritative, Acyclic)
The Core DAG defines the authoritative SDLC lifecycle, flowing strictly from **PRD → TSD → ADR → KB**.

### Core Properties
- **Acyclicity:** Enforced by the Orchestrator (per ADR-005).
- **Deterministic Propagation:** Downstream-only transitions.
- **No Gossip:** All communication is explicit and centrally validated.
- **Full Auditability:** All mutations are recorded and reproducible.

### Critical Governance Rule
> **The Orchestrator MUST reject all Core mutations not originating from human-approved ADRs.** This ensures the Core lifecycle remains 100% human-governed.

# 4. Selective Mesh Layer (Extensions & Custom Workflows)
The Mesh Layer supports user-defined document types, lateral workflows, and semantic relationships without affecting the Core DAG.

### Custom Workflows
Custom workflows operate as independent DAGs within the Mesh Extension Layer and do not modify or extend the Core SDLC DAG. (See Appendix A).

### Mesh Characteristics
- All extensions must declare their schema and are validated by the Orchestrator and Governor.
- The Mesh cannot mutate or override Core nodes or their lifecycle transitions.

# 5. Event-Based Observer Layer
An immutable, append-only event stream (per ADR-002) that provides full system observability. This maintains a strict separation between **structure** (graph) and **behavior** (events).

# 6. Rationale
The hybrid model is the only one that supports both **formal lifecycle guarantees** and **flexible extensibility**.

# 7. Decision Outcome
**Accepted.** This ADR establishes the foundational architecture of SDLC_IDE.

# 8. Dependencies & Cross-References
This ADR is foundational. It is depended upon by ADR-002 (Events), ADR-003 (Embeddings), ADR-004 (Persistence), ADR-005 (Orchestrator), and ADR-006 (Custom Docs).

---

## Appendix A — Custom Workflow Registration & Enforcement
- **Summary:** Teams may register custom SDLC workflows via a declarative registry.
- **Validation:** The Orchestrator validates all workflows for acyclicity, type safety, and ACLs before activation.
- **Governance:** Workflow changes are PR-based and governed by OPA policy.
