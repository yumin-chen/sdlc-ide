ADR 002: Mapping Hidden JJ Operations to SDLC‑IDE Structured Events

Status: Proposed
Date: 2025-11-29
Decision Maker(s): SDLC‑IDE Architecture Team

⸻

Context

Following ADR 001, we now have a hidden JJ workspace providing safe undo/redo, experimental branches, and history rewriting.

To maintain traceability, governance, and MAS-driven workflows, JJ operations must be:
	•	Transparent to the SDLC‑IDE event system
	•	Versioned semantically
	•	Governed by agents for policy enforcement

Direct exposure of JJ metadata is prohibited; only structured events are visible.

⸻

Decision

All JJ operations in the hidden workspace will generate structured, versioned events following SDLC‑IDE schema conventions. MAS agents and CI/CD systems will consume these events.

Event Mapping

| JJ Operation | Event Type | Description | Consumed By |
| :--- | :--- | :--- | :--- |
| undo() | JJ_Undo.v1 | Reverts the last commit or staged change | Governance Agent, Code Agent, CI |
| redo() | JJ_Redo.v1 | Reapplies the last undone change | Governance Agent, Code Agent, CI |
| create_temp_branch() | JJ_Branch_Create.v1 | Creates an experimental branch in JJ workspace | Code Agent, Review Agent |
| merge_temp_branch() | JJ_Branch_Merge.v1 | Merges temporary branch into main workspace | Governance Agent, CI |
| commit() | JJ_Commit.v1 | Commits changes in hidden JJ workspace | Event Inspector, Vectorization Agent |
| rebase() | JJ_Rebase.v1 | Rewrites history of a branch safely | Governance Agent, Review Agent |
| snapshot() | JJ_Snapshot.v1 | Captures current JJ state for traceability | Vectorization Agent, CI |


⸻

Event Schema Example

{
  "type": "JJ_Undo.v1",
  "ts": "2025-11-29T11:00:00Z",
  "eventId": "evt-000123",
  "user": "alice",
  "files_changed": [
    "src/module_a.py",
    "tests/test_module_a.py"
  ],
  "metadata": {
    "reason": "rollback failed merge",
    "jj_commit_id": "abc123def"
  }
}

Rules:
	•	Events are backward compatible (v1, v2 for breaking changes)
	•	All events use fixed fields and disallow undeclared properties (additionalProperties: false)
	•	Events are stored in the SDLC‑IDE event journal (Redpanda, NATS, or local journal)
	•	MAS agents react only to structured events, never directly to JJ state

⸻

MAS Agent Responsibilities

| Agent | Responsibilities with JJ Events |
| :--- | :--- |
| Code Agent | Initiate JJ operations (undo, redo, branch creation) based on workflow or user request |
| Governance Agent | Validate JJ operations against policy, ensure undo/redo complies with branch rules |
| Review Agent | Analyze JJ branch changes, verify compliance before merge |
| Vectorization Agent | Create semantic embeddings of JJ-generated artifacts/events for search/traceability |
| Orchestrator Agent | Schedule JJ operations, coordinate event sequencing |
| Event Inspector | Log and visualize JJ operations in the event timeline |


⸻

Consequences

Benefits:
	•	Fully auditable JJ operations without exposing workspace metadata
	•	MAS-driven governance and policy enforcement
	•	Event-driven integration ensures traceability and CI/CD validation
	•	Users remain unaware of hidden workspace, simplifying DX

Risks:
	•	Additional layer of complexity (wrapper + event generation)
	•	Latency in syncing JJ operations to Git-visible workspace and event system
	•	Requires MAS agents to handle failures and event retries

Mitigations:
	•	Use reliable event journal (Redpanda/NATS/local)
	•	Implement transactional sync: JJ workspace → events → Git workspace
	•	Maintain wrapper CLI/API with strict validation

⸻

Decision Outcome

All hidden JJ operations must generate structured, versioned events according to SDLC‑IDE conventions. MAS agents and CI/CD pipelines will consume these events to maintain governance, traceability, and auditability, while keeping the JJ workspace fully hidden from developers.
