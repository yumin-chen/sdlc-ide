---
title: Validation Agent (Semantic Linter)
status: Proposed
date: 2025-11-27
author: System Architecture Team
project: SDLC_IDE
---

# ADR-005: Validation Agent (Semantic Linter)

## 1. Context
In a multi-agent SDLC system, documents (PRD, TSD, ADR) are created by different actors (humans and agents) at different times. This creates a risk of **Semantic Drift**:
- **Contradictions:** TSD specifies "Eventual Consistency" while PRD demands "Real-time Strong Consistency".
- **Incompleteness:** TSD fails to address a "Security Requirement" listed in the PRD.
- **Implementation Drift:** Codebase evolves away from the TSD/ADR specifications.

ADR-001 (Hybrid Graph) ensures *structural* integrity (DAG).
ADR-009 (Embeddings) provides the *mechanism* for comparison.
**We lack the active agent** responsible for performing these checks and enforcing consistency.

## 2. Decision
We will implement a **Validation Agent** (Tier 2 Intelligence Agent) that acts as a "Semantic Linter" for the SDLC.

### A. Responsibilities
The Validation Agent is a background worker that:
1.  **Listens** to `*_Updated` events (from ADR-002).
2.  **Retrieves** the relevant artifacts and their Dual-Embeddings (from ADR-009).
3.  **Performs** cross-check logic (LLM + Vector Similarity).
4.  **Emits** `Validation_Result` events (Pass, Warning, Fail).

### B. Validation Logic (The "Cross-Check")

#### 1. Completeness Check (PRD → TSD)
*   **Trigger:** `TSD_Updated`
*   **Logic:** For every "Requirement" section in the PRD, does the TSD have a corresponding "Component" or "Design" section with high semantic similarity?
*   **Failure:** "TSD is missing a design for requirement: 'GDPR Compliance'."

#### 2. Contradiction Check (PRD ↔ TSD ↔ ADR)
*   **Trigger:** Any Update
*   **Logic:** Compare "Non-Functional Requirements" (NFRs) across documents.
*   **Failure:** "Conflict detected: PRD asks for < 100ms latency, but ADR-002 accepts > 500ms for Event Layer."

#### 3. Drift Check (TSD ↔ Code)
*   **Trigger:** `Git_Commit` (on main)
*   **Logic:** Compare TSD structural embeddings against generated code summaries.
*   **Failure:** "Implementation drift: New API endpoint `/delete-user` exists in code but is not defined in TSD."

### C. Enforcement Policy
The Validation Agent **does not block** the DAG directly (to avoid paralysis). Instead, it integrates via the **Orchestrator (ADR-003)**:

1.  **Draft State:** Validation failures are posted as **Comments/Warnings** in the IDE/PR.
2.  **Merge State:** Orchestrator's OPA policy can be configured to **Block Merge** if critical validation failures exist (e.g., "Contradiction" = Block, "Incompleteness" = Warn).

## 3. Rationale
*   **Why an Agent?** Validation is computationally expensive (LLM calls) and asynchronous. It shouldn't block the editor UI.
*   **Why Semantic?** Keyword matching fails on "fast" vs "low latency". Embeddings capture the intent.
*   **Why separate from Orchestrator?** Orchestrator handles *process* (ACLs, workflow). Validation Agent handles *content* (meaning).

## 4. Consequences
### Positive
*   **Early Detection:** Conflicts caught at design time, not production.
*   **Living Documentation:** Forces docs to stay in sync with code (Drift Check).
*   **Trust:** Increases confidence that the TSD actually reflects the PRD.

### Negative
*   **False Positives:** LLMs can hallucinate contradictions. (Mitigation: Human override mechanism via "WontFix" labels).
*   **Cost:** Continuous validation consumes token/compute budget.

## 5. Implementation Roadmap
1.  **Phase 1:** Implement "Completeness Check" (PRD → TSD) using simple vector similarity coverage.
2.  **Phase 2:** Implement "Contradiction Check" using LLM reasoning over retrieved sections.
3.  **Phase 3:** Integrate with OPA to block merges on critical failures.
