---
title: "ADR-001: Hybrid Directed Graph Architecture (Revised)"
status: Accepted
date: 2025-11-27
updated: 2025-11-27
supersedes: "Previous draft of ADR-001"
authors: "Yumin Chen, ChatGPT"
---

# ADR-001: Hybrid Directed Graph Architecture (Revised)

## 1. Decision

We adopt a **Hybrid Directed Graph Architecture** that treats the MAS-powered IDE’s knowledge space as two interconnected but independently constrained sub-graphs: a **Core SDLC DAG** and an **Extension Mesh**.

```mermaid
graph TD
    subgraph CoreDAG ["Core SDLC DAG (Acyclic, Authoritative)"]
        direction LR
        PRD --> TSD --> Code --> Test
    end

    subgraph ExtensionMesh ["Extension Mesh (Cycles Allowed)"]
        direction C
        AgentInsight(Agent Insight)
        Risk(Risk Note)
        Compliance(Compliance Tag)

        AgentInsight -- links to --> Risk
        Risk -- triggers --> AgentInsight
        Compliance -- annotates --> TSD
        AgentInsight -- references --> Code
    end
```
*The diagram above illustrates the default SDLC workflow. The Core DAG is configurable to support user-defined workflows.*

### 1.1. The Core SDLC DAG (Canonical, Acyclic, Authoritative)
This sub-graph represents the strict manufacturing pipeline of software engineering artifacts. The system supports **user-defined custom workflows**, with a default sequence of `PRD` → `TSD` → `Code` → `Test`.

**Key Properties:**
- **Acyclic:** No downstream artifact may depend on one of its transitive descendants. This is the primary structural invariant.
- **Canonical:** Exactly one canonical instance of each core artifact (unique `artifact_id`).
- **Strict Lineage:** Each document explicitly declares its upstream dependencies.
- **Composable:** Artifacts may depend on multiple upstream items, as long as acyclicity holds.

### 1.2. The Extension Mesh (Flexible, Multi-Parent, Unconstrained)
Extensions represent integrations, plugins, domain-specific documents, agent-produced insights, and system-level annotations.

**Key Properties:**
- **Mesh-like:** Arbitrary many-to-many connections.
- **No Acyclicity Requirement:** Cycles are permitted.
- **Type-Safe Edges:** Each extension type defines its allowed upstream artifact types.
- **Non-Authoritative:** Extension nodes annotate but do not override canonical artifacts.

### 1.3. Unified View
While the DAG and Mesh have distinct rules, the system presents them as a unified artifact graph for users, agents, and analysis.

### 1.4. Enforcement
Graph rules are declared here, but enforcement mechanisms are defined in other ADRs:
- **ADR-005 (Orchestrator):** Enforces the invariants and rules defined in this ADR.
- **ADR-004 (Persistence Layer):** Defines how graph edges are stored.

## 2. Motivation

The system requires:
- A reliable but **configurable** core dependency structure for the SDLC's causal chain.
- A flexible augmentation layer for agents, analytics, and domain-specific metadata.
- A unified graph API supporting vector search, impact analysis, and multi-agent collaboration.
- A clear separation of concerns between the graph's definition (this ADR), its enforcement (Orchestrator), and its storage (Persistence).

## 3. Detailed Design

### 3.1. Artifact Types
Artifacts belong to one of two families:
- **Core Artifacts (DAG):** PRD, TSD, ADR, Code, Test, Design, DeploymentPlan, etc.
- **Extension Artifacts (Mesh):** AgentInsight, Contradiction, RiskNote, ComplianceTag, domain-specific specs, and code intelligence nodes.

### 3.2. Allowed Edges

**DAG Edges**

The primary rule for the Core DAG is that **all connections must maintain acyclicity**. While the system supports custom workflows, the default workflow establishes the following allowed edges:

| From | To   | Rule (Default Workflow)                   |
| :--- | :--- | :---------------------------------------- |
| PRD  | TSD  | Allowed                                   |
| TSD  | Code | Allowed                                   |
| Code | Test | Allowed                                   |
| Any  | Any  | Allowed if and only if acyclicity is preserved. |

**Mesh Edges**

| From          | To                               | Rule                               |
| :------------ | :------------------------------- | :--------------------------------- |
| Any extension | Any artifact (core or extension) | Allowed if type rules match.       |
| Cycles        | Allowed                          | Cycles are permitted within the mesh. |

*Note: Mesh edges may form cycles among extension artifacts, but they must not create a cycle that involves any part of the Core DAG.*

### 3.3. Invariants
- Core artifacts must form a Directed Acyclic Graph.
- Extension artifacts must not affect the acyclicity of the Core DAG.
- Each artifact has exactly one canonical lineage declaration.
- Only the Orchestrator may modify lineage metadata (see ADR-005).
- Storage of edges is defined in ADR-004.

## 4. Rejected Alternatives

### 4.1. Single Global DAG
- **Rejected because:** Too rigid. It would force extension artifacts into artificial acyclic structures and prevent natural feedback loops common in metadata graphs.

### 4.2. Fully Unrestricted Global Graph
- **Rejected because:** Too chaotic. The strict, predictable lineage of the SDLC would be unenforceable, making impact analysis unreliable.

## 5. Consequences

### Positive
- Clean separation of authoritative lineage vs. annotation.
- Supports both a default workflow and user-defined custom SDLC pipelines.
- The DAG enables safe change propagation, while the Mesh enables flexible domain intelligence.

### Negative / Neutral
- The Orchestrator's complexity increases to manage custom workflows (addressed in ADR-005).
- Tooling must visually distinguish between DAG links (lineage) and Mesh links (annotations).

## 6. Implementation Notes (Non-normative)
- **Persistence:** Format stored in `.sdlc_ide/graph/` (see ADR-004).
- **Validation:** The Orchestrator performs cycle checks on the Core DAG (see ADR-005). Mesh edges are validated by type rules (see ADR-006).
- **Contribution:** Agents contribute mesh nodes via event publishing (see ADR-009).

## 7. Dependencies

- **Depends On:** None — this is a foundational ADR.
- **Depended By:** ADR-002 (Events), ADR-003 (Embeddings), ADR-004 (Persistence), ADR-005 (Orchestrator), ADR-006 (Custom Docs), ADR-009 (Agents), ADR-010 (Vector DB).

## 8. Notes for Future Revisions
- A future ADR may define a formal Graph Query API.
- Temporal graph semantics may be introduced later to support time-travel views.
