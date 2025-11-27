ADR‑004: Unified Memory & Persistence Layer Using a Version‑Controlled Workspace
Status: Draft
Date: 2025‑11‑27
Project: SDLC_IDE
Author: System Architecture Team (via Yumin@Chen.Software)
1. Context
The SDLC_IDE multi‑agent system requires persistent memory across:
Core SDLC agents (PRD → TSD → ADR → KB)
Extension agents (custom document types)
Observers and analytics systems
The Orchestrator and Governor
Vector embeddings, caches, derived artifacts
Agent‑level state (e.g., contradiction history, risk profiles)
Today, agents rely primarily on:
Event streams (Kafka/Pulsar/NATS)
Vector DB queries
In‑memory computations
But there is no unified long‑term persistence layer shared across agents.
We need:

Deterministic, reproducible state
Auditability aligned with SDLC
Human‑accessible persisted data
Agent‑generated artifacts versioned with the system
Compatibility with Git or Jujutsu
A structured folder acting as the “system workspace”
A storage model agents can read/write without tight coupling
Core constraints
The persistence layer must not interfere with the Core DAG semantics
Non‑authoritative caches must be separated from authoritative documents
Must support rollback, branching, and restoration
Must support embedding stores and indexes without bloating version history
Must allow both human‑authored and machine‑authored artifacts
2. Decision
We adopt a unified version‑controlled “System Workspace” directory as the persistence layer for all agents.
A. Workspace Structure
A reserved directory (default: /.sdlc_ide/) will be created inside the root project:
.sdlc_ide/
   core/
      prd/
      tsd/
      adr/
      kb/
   extensions/
   events/
   memory/
      long_term/
      episodic/
      agent_state/
   embeddings/
      index/
      vectors/
   cache/
   logs/
      agent/
      orchestrator/
B. Persistence Rules
Authoritative artifacts (PRD, TSD, ADR, KB)
Stored under core/ and always version‑controlled.
Extension artifacts
Stored under extensions/ with the same rules as core, but governed by the extension mesh policies.
Agent memory
Long‑term memory → version‑controlled
Episodic memory → non‑authoritative (ignored by .gitignore)
Agent state machines and checkpoints → version‑controlled
Embeddings
Raw vectors not stored in Git
Only deterministic indexes, manifests, and metadata versioned
Vectors stored as binary blobs outside Git or in a pluggable Vector DB
Events
Canonical immutable snapshots are optionally saved for audit
Full event logs excluded from Git
C. Git / Jujutsu Integration
Workspace integrates with:
Git
Jujutsu (jj)
Hybrid setups (Git for remote, jj for local)
Agents may:
Open branches (feat/prd-update, agent/contradiction-fix)
Commit machine‑generated updates
Submit changes via PR/MR (enforced by Governor)
All core merges must go through PR/MR workflows.
D. Orchestrator & Governor Roles
Orchestrator
Manages file I/O transactions
Controls which agents can write where
Ensures state persistence is deterministic
Governor (OPA/Rego policies)
Enforces:
“ADR must be merged via PR”
“TSD updates require PRD consistency checks”
“Core DAG write boundaries”
Blocks illegal writes
Ensures compliance before merge
3. Rationale
Why use a version‑controlled workspace?
Benefits:
Full auditability
Deterministic reproducible system state
Unified location for all MAS memory and artifacts
Tracks machine‑generated changes as first‑class citizens
Seamless collaboration with human contributors
Natural fit with the core DAG flow
Easy rollback and snapshotting
Enables multi‑agent branching workflows
Alternatives considered:
Using a DB only → not human‑friendly
Using only vector DB → insufficient for artifacts
Using external storage → breaks reproducibility
This approach unifies file‑based, event‑based, and embedding‑based memory.
4. Consequences
Positive
Transparent stateless deployment (state lives in directory)
Agents can restart and recover cleanly
Simplifies debugging and audits
Reproducible experiments for model tuning
Supports multi‑agent collaboration on Git branches
Negative
Workspace structure adds operational complexity
Requires strict OPA governance to avoid agent file conflicts
Storing long‑term state in Git may generate noise if not managed
Neutral / Tradeoffs
Requires .gitignore discipline
Embeddings stored separately require migration tooling
5. Alternatives Considered
A. Pure Database Persistence
Rejected because:
Opaque to humans
Hard to version
Hard to diff
Not reproducible in Git-based workflows
B. Full External KV Store
Rejected because:
Not compatible with branching/PR workflows
Not integrated with SDLC lifecycle
C. No Persistence Layer (event-based only)
Rejected because:
Agents lose state
Contradiction history cannot accumulate
Debugging becomes almost impossible
6. Decision Outcome
Accepted (pending final review).
SDLC_IDE will adopt a Unified Version‑Controlled Workspace for persistent memory and authoritative system state.

This persistence model becomes foundational for:

All core agents
Extension agents
The Orchestrator
The Governor
The ContradictionDetector
Future AI-based agents
