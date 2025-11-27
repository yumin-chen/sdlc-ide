## 📄 ADR-000: Hybrid Directed Graph Architecture with Selective Mesh Extensions

**Status:** **Accepted**
**Date:** 2025-11-27
**Updated:** 2025-11-27
**Project:** SDLC_IDE
**Author:** System Architecture Team

---

### 1. ⚙️ Context

The **SDLC_IDE** platform needs a **multi-agent architecture** to manage all Software Development Lifecycle (SDLC) artifacts. The design must balance a **strict, auditable core flow** with **safe extensibility**.

#### Core Requirements

* **Document Flow & Determinism:**
    * **Canonical Core Pipeline:** PRD > TSD > ADR > KB.
    * The core **Directed Acyclic Graph (DAG)** must be **acyclic** and **deterministic**.
    * Core agents communicate **downstream only** (no gossip).
* **Extensibility:**
    * Custom document types and relationships are allowed via the **Mesh layer**.
    * The Mesh layer **cannot** alter or introduce cycles into the **Core DAG**.
* **Observability:**
    * All state and structural mutations generate **immutable events**.

---

### 2. 💡 Decision

Adopt a **Hybrid Directed Graph Architecture** with three integrated layers:

1.  **Core Directed Acyclic Graph (DAG):** For strict, deterministic SDLC flow.
2.  **Selective Mesh Extension Layer:** For safe, governed extensibility and semantic linking.
3.  **Event-Based Observer Layer:** For immutable auditability and analytics.

---

### 3. 🎯 Core Directed Acyclic Graph (DAG)

The Core DAG defines the **authoritative SDLC flow**: **PRD > TSD > ADR > KB**.



* **Properties:**
    * **Acyclic** (enforced by Orchestrator - ADR-005).
    * **Deterministic** (strictly ordered life-cycle transitions).
    * **Downstream communication only**.
    * **Single source of truth** for all derived documents.

| Core Agent | Responsibilities |
| :--- | :--- |
| **PRD Manager** | Accepts human PRDs, publishes `PRD_Updated`, writes to workspace. |
| **TSD Manager** | Regenerates/validates TSD after PRD changes; publishes `TSD_Updated`. |
| **ADR Manager** | Updates architectural decisions after TSD changes; publishes `ADR_Updated`. |
| **KB Manager** | Indexes and archives ADR updates; publishes `KB_Updated`. |

**Rationale:** The DAG guarantees **consistent lineage**, prevents upstream mutation, and ensures a verifiable, reproducible SDLC flow.

---

### 4. 🔗 Mesh Extension Layer (Selective, Controlled)

The Mesh supports **custom document types**, **workflows**, and **semantic relationships** while being strictly subordinate to the Core DAG.

* **Capabilities:**
    * User-defined types, schemas, and edges.
    * Many-to-many relationships.
    * **Cycles allowed only within the Mesh**.
    * Optional gossip allowed inside approved mesh clusters.

* **Constraints:**
    * Mesh may reference the **Core**, **never the reverse**.
    * Mesh **cannot modify DAG structure**.
    * All changes are validated by the **Orchestrator** + **Governor**.

**Example Mesh Type Declaration:**
> `{ "type": "ArchitectureDiagram", "schema": "diagram.schema.json", "inbound_edges": ["ADR"], "outbound_edges": [], "embedding_strategy": "structural+image", "lifecycle": "mesh" }`

---

### 5. 📢 Event-Based Observer Layer

A distributed, **append-only event stream** (ADR-002) captures all significant activity for auditability and analysis.

* **Captured Events:** Document lifecycle transitions, agent-to-agent communication, user edits, and structural changes.
* **Properties:** **Immutable**, **non-authoritative** (informational only), and versioned schema.
* **Purpose:** Powers analytics, ML/search functions, and auditing.

---

### 6. ✅ Rationale

The hybrid model is necessary to achieve all core requirements simultaneously.

| Requirement | DAG Only | Mesh Only | **Hybrid** |
| :--- | :--- | :--- | :--- |
| **Strict SDLC flow** | ✅ | ❌ | **✅** |
| **Extensibility** | ❌ | ✅ | **✅** |
| **Predictability** | ✅ | ❌ | **✅** |
| **Semantic linking** | Limited | ✅ | **✅** |
| **Safety & governance** | ✅ | ❌ | **✅** |
| **Auditability** | ✅ | ❌ | **✅** |

---

### 7. ⚖️ Consequences & Tradeoffs

| Category | Description |
| :--- | :--- |
| **Positive** | Deterministic core flow; rich extensibility with safe boundaries; high visibility through events; Mesh enables domain-specific modeling without destabilizing the DAG. |
| **Negative** | Increased implementation complexity (validation, schemas, ACLs); Strict declaration overhead for custom types. |
| **Tradeoff** | **Flexibility is allowed but never unrestricted.** Every structural mutation must pass Orchestrator validation. |

---

### 8. 🔄 Alternatives Considered

* **Full DAG:** Too rigid for semantic or domain-specific documents.
* **Full Mesh:** Cannot enforce SDLC lifecycles or safety guarantees.
* **Hub-and-Spoke:** Centralized bottleneck; lacks semantic flexibility.
* **Decision:** Hybrid architecture.

---

### 9. ➡️ Cross-References

* **Depends on:** None
* **Depended by:** ADR-002 > ADR-007
* **Relevant ADR Links:** ADR-002 (Event Streaming), ADR-005 (Orchestrator & Governor), ADR-006 (Custom Document Types), ADR-004 (Persistent Workspace).

---

### 10. ❓ Open Questions (To Be Finalized in Dependent ADRs)

| Question | ADR | Status |
| :--- | :--- | :--- |
| Mesh edge validation | ADR-005 | Pending |
| ACL / Policy model | ADR-005/006 | Pending |
| Workspace consistency rules | ADR-004 | Pending |
| Transaction model | ADR-004/005 | Pending |
| Custom type registration | ADR-006 | Pending |
| Failure mode interactions | ADR-007 | Pending |

---

### 11. 📖 Glossary

| Term | Definition |
| :--- | :--- |
| **DAG** | Core SDLC lineage; strict, acyclic flow. |
| **Mesh** | Extensible semantic graph; cycles allowed. |
| **Orchestrator** | Structure-enforcing controller (ADR-005). |
| **Governor** | Policy engine (OPA/Rego). |
| **Event** | Immutable record in event log (ADR-002). |
| **Workspace** | Version-controlled storage (`.sdlc_ide/`). |
| **Gossip** | P2P communication; allowed only in mesh clusters. |

---

### 12. 📝 Example Core DAG Transition

1.  User edits **PRD-42**.
2.  Orchestrator receives `PRD_Updated`.
3.  Marks **TSD-42** as `pending_sync`.
4.  TSD Manager regenerates > publishes `TSD_Updated`.
5.  ADR Manager updates > publishes `ADR_Updated`.
6.  KB Manager indexes > publishes `KB_Updated`.

**Result:** Fully consistent PRD > TSD > ADR > KB chain.
