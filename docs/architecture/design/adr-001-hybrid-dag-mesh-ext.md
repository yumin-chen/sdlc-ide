---
title: "ADR-001: Hybrid DAG & Mesh Extension Architecture"
status: Accepted
date: 2025-11-27
updated: 2025-11-27
authors: "System Architecture Team (via Yumin@Chen.Software)"
project: SDLC_IDE
---

# 1. Context
The SDLC_IDE platform requires a multi-agent architecture capable of safely managing all SDLC artifacts. The system needs to preserve deterministic, auditable lifecycle transitions for a canonical SDLC pipeline, while also supporting user-defined custom workflows registered through a declarative mechanism.

The platform must support:
- Strict communication boundaries between core document managers
- Deterministic, auditable lifecycle transitions
- User-defined workflow pipelines that remain safe and acyclic
- Extensible domain modeling through custom document types and schemas
- AI-assisted analysis via embeddings and event observations
- Central governance via an Orchestrator that enforces structural, policy, and security guarantees

### Core Constraints
- The Core DAG is always acyclic.
- The system provides a default canonical pipeline: `PRD → TSD → ADR → KB`
- Teams may register custom pipelines through the workflow registry.
- Extensions must never destabilize or introduce cycles into the Core DAG.
- Agent communication must enforce:
    - Determinism
    - Predictability
    - Security
    - Zero implicit propagation

### Architectural Question
How can SDLC_IDE enforce strict and auditable SDLC governance while still allowing teams to define flexible, domain-specific workflows and semantic extensions?

**Conclusion:** Adopt a Hybrid Directed Graph Architecture.

# 2. Decision
SDLC_IDE will adopt a Hybrid Directed Graph Architecture consisting of:
- **Core Directed Acyclic Graph (DAG)** — The authoritative SDLC lifecycle, with a default pipeline and support for user-defined custom pipelines.
- **Mesh Extension Layer** — Flexible semantic documents and relations outside the Core lifecycle.
- **Event-Based Observer Layer** — Event stream for analytics, monitoring, embeddings, and ML signals.
- **Central Orchestrator** — Governs all graph mutations, workflow validation, and policy enforcement.

# 3. Core DAG (Authoritative, Acyclic)
The Core DAG encodes the SDLC workflow. Its primary invariant is acyclicity.

### Default Pipeline
The system provides the canonical flow: `PRD → TSD → ADR → KB`

### Custom Pipelines
Teams may register alternative workflows via the Workflow Registry (details in Appendix A). The Orchestrator enforces:
- Acyclicity
- Valid artifact types
- Permissions (OPA)
- Backwards compatibility on workflow changes

### Core DAG Guarantees
- No cycles, no lateral gossip
- Deterministic propagation
- Explicit transitions only
- Fully governed by the Orchestrator
- Predictable and auditable evolution
- Workflow‑level safety for both default and custom pipelines

The Core DAG is the authoritative structural backbone of SDLC_IDE.

# 4. Mesh Extension Layer (Flexible, User‑Defined)
The Mesh Layer allows arbitrary, user‑defined:
- Document types & Schemas
- Many‑to‑many semantic edges
- Analysis artifacts & Compliance modules
- API specs & Performance models
- Domain‑specific extension types

### Mesh Characteristics
- Cycles allowed (but only within Mesh nodes)
- No Mesh element may become a dependency of a Core node
- Mesh may annotate or reference Core artifacts, but cannot modify Core structure
- Edges validated by Orchestrator (rules formalized in ADR‑004)

# 5. Event‑Based Observer Layer
A distributed event system captures:
- Document lifecycle events
- Version updates
- Agent communication
- Embedding recalculations
- Workflow changes
- Policy evaluation signals

### Event Layer Guarantees
- Cannot alter Core DAG or Mesh topology
- Purely observational
- Drives analytics, ML recommendations, semantic search, and personalization

*Events reflect behavior, not structure.*

# 6. Rationale
A pure DAG is overly restrictive; a pure mesh is unsafe for lifecycle governance.

| Requirement | DAG | Mesh | Hybrid |
| :--- | :---: | :---: | :---: |
| Strict SDLC flow | ✔️ | ✖️ | ✔️ |
| Extensibility | ✖️ | ✔️ | ✔️ |
| Predictability | ✔️ | ✖️ | ✔️ |
| Semantic linking | Limited | ✔️ | ✔️ |
| Policy enforcement | ✔️ | Risky | ✔️ |

The hybrid architecture meets all SDLC_IDE objectives.

# 7. Consequences
- **Positive:** Strong governance, deterministic SDLC flow with validated custom pipelines, and safe extensibility.
- **Negative:** Increased complexity in orchestrator logic; requires schema definitions for mesh nodes.
- **Tradeoffs:** All structural mutations flow through the Orchestrator; UI must clearly distinguish core lineage vs. semantic relations.

# 8. Alternatives Considered
- **❌ A. Full DAG Only:** Too rigid; cannot support mesh-like semantic relationships.
- **❌ B. Full Mesh Only:** No ability to enforce SDLC rules; easy to introduce cycles; unsafe for compliance.
- **❌ C. Hub-and-Spoke:** Orchestrator bottleneck; insufficient semantic flexibility.

# 9. Decision Outcome
**Accepted.** SDLC_IDE will implement:
1. Core DAG (strict, acyclic, user-configurable workflows)
2. Mesh Extension Layer (flexible semantic graph)
3. Event Observer Layer (analytics + ML)
4. Orchestrator enforcing all structural and policy rules

This ADR is the foundational architecture of SDLC_IDE.

---

## Appendix A — Custom Workflow Registration & Enforcement

### Summary
The system ships with a default canonical pipeline (`PRD → TSD → ADR → KB`). Teams may register custom pipelines through a declarative workflow registry. The Orchestrator validates all workflows before activation.

### Workflow Registration
- **File Location:** `.sdlc_ide/workflows/<workflow-id>.yaml`
- **File Requirements:** Each workflow file must include `id`, `version`, `author`, `status` (`draft` | `active` | `deprecated`), `scope`, `nodes`, and `edges`.

### Validation Rules
The Orchestrator enforces:
- **Acyclicity:** DAG topological validation.
- **Type Safety:** All nodes must map to known artifact types.
- **ACLs & Permissions:** Validated via OPA.
- **Backward Compatibility:** Workflow changes must not invalidate existing artifacts and require explicit migration plans.

### Activation Lifecycle
1. Custom workflow PR is submitted.
2. CI validates structure + OPA policy.
3. On merge, Orchestrator performs final validation.
4. Workflow status is set to `active`.
5. Activation event is recorded in the event stream for full regulatory traceability.
