ADR 001: Hidden Jujutsu Workspace Integration for Safe Undo/Redo

Status: Proposed
Date: 2025-11-29
Decision Maker(s): SDLC‑IDE Architecture Team

⸻

Context

The SDLC‑IDE is a multi-agent, event-driven development environment with:
	•	Document-first workflow (PRD → TSD → artifacts → code)
	•	Strong governance and traceability via structured events
	•	CI/CD enforcing policy, schema, and event validation
	•	Non-US, open, local-first technology stack

We want to integrate Jujutsu (JJ) to leverage its operation-based version control for:
	•	Safe undo/redo of changes
	•	Temporary experimental branches
	•	History rewriting for agent-driven workflows

However, direct use of JJ in a colocated Git workspace can lead to confusing states when interleaving Git and JJ operations.

⸻

Decision

Introduce a hidden/shadow JJ workspace that is fully isolated from the main Git workspace. Users and agents interact with JJ exclusively through a controlled interface, exposing only safe operations and generating structured events.

Key elements:
	1.	Hidden Workspace
	•	Location: .jj_shadow/ within project or /tmp/jj_workspace
	•	Initialized from the current Git repository
	•	Contains full JJ repository for commits, branches, and history rewriting
	2.	Controlled Interface
	•	CLI/API wrapper exposing safe operations:
	•	undo()
	•	redo()
	•	create_temp_branch()
	•	merge_temp_branch()
	•	Interface applies changes back to visible Git workspace after each operation
	3.	Event-Driven Integration
	•	Each JJ operation emits structured events:

{
  "type": "JJ_Undo.v1",
  "ts": "2025-11-29T10:00:00Z",
  "metadata": { "user": "alice", "files_changed": 3 }
}


	•	MAS agents subscribe to these events for governance, traceability, and CI/CD validation

	4.	MAS and Agent Use
	•	Agents (Code Agent, Governance Agent) can invoke JJ operations programmatically
	•	Users do not interact with JJ directly, reducing risk of misoperation
	5.	Synchronization
	•	Changes in JJ workspace are safely synchronized to Git workspace:
	•	Undo/redo operations modify working files
	•	Temporary branches can be exported as standard Git branches
	•	Ensures Git workspace remains clean, linear, and compatible with external tooling

⸻

Consequences

Benefits
	•	Safe operation-based version control with undo/redo and experimental branches
	•	Fully traceable and auditable operations via structured events
	•	Maintains user-facing Git workspace simplicity
	•	MAS agents can leverage JJ safely for automated workflows

Drawbacks / Risks
	•	Additional complexity in maintaining a hidden JJ workspace
	•	Slight latency due to sync between JJ workspace and Git workspace
	•	Requires disciplined wrapper interface to prevent accidental direct JJ usage

Mitigations
	•	Enforce wrapper interface usage via policy and CI/CD checks
	•	Keep hidden workspace location configurable and ephemeral if needed
	•	Generate structured events for all JJ operations to maintain auditability

⸻

Alternatives Considered
	1.	Colocated JJ + Git
	•	Pros: Direct access to JJ in repo
	•	Cons: High risk of inconsistent states, confusing for users
	2.	Pure Git without JJ
	•	Pros: Simple, familiar
	•	Cons: No safe undo/redo, no operation-based history rewriting
	3.	Hybrid / API-layer isolation (chosen)
	•	Pros: Safe, transparent, auditable, preserves Git simplicity
	•	Cons: Slight additional infrastructure overhead

⸻

Decision Outcome

Adopt a hidden JJ workspace with controlled interface for undo/redo and experimental history operations, fully integrated into the SDLC‑IDE MAS and event-driven pipeline.
