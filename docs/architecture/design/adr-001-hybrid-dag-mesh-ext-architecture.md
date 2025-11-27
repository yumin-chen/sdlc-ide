---
title: "ADR-001: Hybrid Directed Graph Architecture"
status: Accepted
date: 2025-11-27
project: SDLC_IDE
author: System Architecture Team
---

# 1. Context

The SDLC_IDE platform requires a multi-agent architecture capable of managing heterogeneous documentation types across the SDLC lifecycle while maintaining strict structural guarantees. The architecture must support:

*   Clear upstream → downstream communication boundaries between core document managers.
*   Deterministic and auditable lifecycle transitions.
*   User-defined extensions without compromising core SDLC integrity.
*   Immutable observability of all state changes.
*   A safe, governed environment for extensibility.

---

# 2. Decision

We will adopt a **Hybrid Directed Graph Architecture** with four primary components: a Core Directed Acyclic Graph (DAG) for authoritative artifacts, a Selective Mesh Layer for flexible extensions, an Event-Based Observer Layer for monitoring, and a dual governance model consisting of an Orchestrator (for structural validation) and a Governor (for policy enforcement).

---

## A. Core Strict Directed Acyclic Graph (DAG)

Defines the authoritative SDLC lifecycle (e.g., **PRD → TSD → ADR → KB**).

#### Properties
*   **Acyclic:** Enforced by the Orchestrator (ADR-005).
*   **Deterministic:** Enables reproducible builds and compliance.
*   **Immutable Core:** The Orchestrator MUST reject all Core mutations not originating from a human-approved ADR.

---

## B. Selective Mesh Layer (Extensions)

Supports user-defined document types, semantic relations, and lateral workflows.

#### Characteristics
*   All custom types must declare a schema, allowed edges, and lifecycle state.
*   Mesh edges can connect to the Core DAG but cannot mutate core nodes.
*   All extensions are validated by the Orchestrator.

---

## C. Event-Based Observer Layer

An immutable, append-only event stream (per ADR-002) for analytics, search, and replay. It is strictly observational and not authoritative for state.

---

# 3. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph CoreDAG ["Core DAG (Authoritative SDLC Pipeline)"]
        direction TB
        PRD[PRD Manager] --> TSD[TSD Manager]
        TSD --> ADR[ADR Manager]
        ADR --> KB[Knowledge Manager]
    end

    subgraph Mesh ["Mesh Extensions (Flexible, User-Defined)"]
        direction TB
        Comp[Compliance Module] & API[API Spec]
    end

    subgraph Gov ["Governance & Observation"]
        Orch[Orchestrator]
        Govr[Governor (OPA/Rego)]
        Events[Event Stream]
    end

    TSD -.-> API
    PRD -.-> Comp
    Orch -- Governs --> CoreDAG
    Orch -- Validates --> Mesh
    Govr -- Policy --> Orch
```

---

# 4. Rationale

A pure DAG is too rigid for modern SDLC needs, while a pure Mesh is too chaotic and ungovernable. The hybrid approach provides the optimal balance of strong guarantees and flexible extensibility.

---

# 5. Consequences

*   **Positive:** Strong governance, deterministic state transitions, and safe integration of custom document types.
*   **Negative:** Increased complexity in the Orchestrator, which must manage both DAG and Mesh validations.

---

# 6. Alternatives Considered

*   **Full DAG:** Rejected — too rigid.
*   **Full Mesh:** Rejected — unsafe and ungovernable.
*   **Hub-and-Spoke:** Rejected — creates a central bottleneck.

---

# 7. Decision Outcome

**Accepted.** This ADR establishes the foundational architecture for the SDLC_IDE platform.

---

# 8. Dependencies & Cross-References

**Depends On:** None (foundational)

**Depended By:**
*   ADR-002: Event Streaming
*   ADR-003: Vectorization
*   ADR-004: Persistence
*   ADR-005: Orchestrator
*   ADR-006: Custom Document Types
*   ADR-007: Failure Modes
*   ADR-010: Autonomous Mesh Extension Pipeline

---
