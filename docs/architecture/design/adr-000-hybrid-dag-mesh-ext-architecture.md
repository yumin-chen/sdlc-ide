---
title: Hybrid Directed Graph Architecture with Selective Mesh Extensions
status: Draft
date: 2025-11-27
authors: System Architecture Team (via Yumin@Chen.Software)
project: SDLC_IDE
---

# ADR‑000: Hybrid Directed Graph Architecture with Selective Mesh Extensions

---

# 1. Context

The SDLC_IDE platform requires a multi‑agent architecture capable of managing SDLC artifacts under strict lifecycle governance while supporting user‑defined custom workflows and autonomous Mesh extensions.

The system must:

- Manage all documentation types across the SDLC lifecycle  
- Enforce strict communication boundaries among core document managers  
- Maintain deterministic, auditable lifecycle transitions  
- Allow custom document types without compromising core flow  
- Support AI‑driven analytics and semantic embeddings  
- Provide safe, governed extensibility via declarative Mesh models

### Key Constraints

**Document & Communication Rules**

- PRD remains human‑authored; TSD must be machine‑validated  
- Core document agents follow **strict one‑way flow:**  
  **PRD → TSD → ADR → KB**  
- No cycles allowed in core flow  
- Communication boundaries must be deterministic and enforceable

**Extensibility Rules**

- Extensions (custom types, agents, workflows) must be declarative  
- Extensions may not create cycles or mutate core artifacts  
- Schema, edges, and lineage must be explicit  
- Validation must run through the Orchestrator

**Observability & State**

- All state changes must be logged to immutable event streams  
- Semantic inferences (vector embeddings) cannot override structural rules  
- Persistent workspace must maintain DAG semantics across restarts

---

# 2. Decision

Adopt a **Hybrid Directed Graph Architecture** comprised of:

1. **Core Strict DAG**  
2. **Selective Mesh Layer (Extensions)**  
3. **Event‑Based Observer Layer**

---

## A. Core Strict Directed Acyclic Graph (DAG)

Defines the authoritative SDLC flow:

**Flow:**  
**PRD → TSD → ADR → KB**

**Properties**

- Acyclic; validated by the Orchestrator (ADR‑005)  
- Deterministic propagation  
- Strict downstream‑only communication  
- Compliance‑friendly state transitions  
- No gossiping; only explicit, orchestrated messages

**Core Agent Responsibilities**

| Agent | Responsibilities |
|-------|------------------|
| **PRD Manager** | Accept PRDs; publish `PRD_Updated`; persist to workspace |
| **TSD Manager** | Validate against PRD; publish `TSD_Updated`; persist |
| **ADR Manager** | Validate against TSD; publish `ADR_Updated`; persist |
| **KB Manager** | Index and store knowledge; publish `KB_Updated` |

---

## B. Selective Mesh Layer (Extensions)

Supports safe user‑defined workflows.

**Characteristics**

- Explicit declaration: schema, allowed edges, embedding strategy, lifecycle  
- Orthogonal to the Core DAG  
- Cannot mutate core artifacts  
- Cannot create cycles  
- Optional gossiping **within approved Mesh clusters only**  
- Semantic linking via embeddings (ADR‑003), but structural rules dominate

**Example Mesh Extension**

```json
{
  "type": "ArchitectureDiagram",
  "schema": "diagram.schema.json",
  "inbound_edges": ["ADR"],
  "outbound_edges": [],
  "embedding_strategy": "structural+image",
  "lifecycle": "mesh"
}
