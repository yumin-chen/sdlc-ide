---
title: "ADR-010: Autonomous Mesh Extension Architecture"
status: Proposed
date: 2025-11-27
project: SDLC_IDE
author: System Architecture Team
---

# 1. Context
This ADR defines the architecture for how the SDLC_IDE system can autonomously evolve its Mesh layer. Building on the foundational Hybrid Directed Graph Architecture defined in ADR-001, this document specifies a safe, governed pipeline for agents to propose and register new Mesh-level document types and relationships at runtime.

# 2. Decision
We will implement a **Self-Proposing Extensions Architecture**. This model allows agents to discover needs and generate proposals, which are then validated through a mandatory two-stage process (structural and policy) before being autonomously registered. **The Core DAG remains immutable and cannot be altered by this process.**

# 3. The 5-Stage Autonomous Extension Pipeline
1.  **Discovery:** Agents analyze system behavior, document patterns, and user workflows to detect emergent needs and generate a **Draft Extension Proposal (DEP)**.
2.  **Proposal Generation:** Agents generate a formal **Mesh Extension Spec (MES)**, including schema, allowed edges, and intended semantics.
3.  **Structural Validation (Orchestrator):** The Orchestrator (per ADR-005) enforces structural invariants, including cycle detection, DAG boundary protection, and topological safety.
4.  **Policy & ACL Validation (Governor / OPA):** The Governor (per ADR-005) enforces non-structural rules, such as access control, compliance requirements, and semantic policies.
5.  **Autonomous Registration:** If both the Orchestrator and Governor approve, the new Mesh type is registered in the **Mesh Registry**, making it available at runtime.

# 4. Safety & Governance Constraints
- Autonomous agents **MUST NOT** mutate or propose Core DAG changes.
- All extension proposals, approvals, and rejections **MUST** be emitted as immutable events for auditing (per ADR-002).
- Only humans, via the formal ADR governance process, may modify the Core DAG structure.

# 5. Diagram of the Proposal Pipeline
```mermaid
graph TD
    A[Autonomous Agents<br/>(Discovery & Proposal Gen)] --> B(Mesh Extension Spec);
    B --> C{Validation};
    C --> D[ORCHESTRATOR<br/>Structural Rules];
    C --> E[GOVERNOR<br/>Policy + ACLs];
    D --> F{Result};
    E --> F;
    F -- Pass --> G[MESH REGISTRY<br/>(Dynamic Types)];
    G --> H(Runtime Mesh Layer);
    F -- Fail --> I([Proposal Rejected]);
```
