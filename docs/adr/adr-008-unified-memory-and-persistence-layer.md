# ADR-008: Unified Memory & Persistence Layer

## Status

Draft

## Context

ADRs 001-003 describe the system's dynamics (DAG, events, embeddings), but do not specify where the state of the system actually lives. This ADR fills that void by defining a unified persistence model that accommodates both human- and machine-generated artifacts within a version-controlled workspace. This approach ensures that all components, including agent-generated artifacts, are treated as first-class citizens, which simplifies debugging, auditing, and reproducibility.

## Decision

The system will adopt a version-controlled workspace, managed by the Orchestrator, with a well-defined directory structure. This workspace will be backed by a version control system like Git or Jujutsu, allowing for branching, merging, and rollbacks. The structure separates authoritative, version-controlled documents from non-authoritative caches and transient data.

### Workspace Structure

```
.
├── .sdlc_ide/
│   ├── snapshots/
│   ├── tmp/
│   └── logs/
│       ├── wal.jsonl
│       ├── audit_trail.jsonl
│       └── merge_conflicts.jsonl
├── core/
│   ├── prd/
│   ├── tsd/
│   ├── adr/
│   └── kb/
├── extensions/
├── memory/
│   ├── long_term/
│   ├── episodic/
│   └── agent_state/
├── embeddings/
│   ├── index/
│   └── vectors/
├── cache/
└── .gitignore
```

---

## Specifications

### 1. Authoritative vs. Non-Authoritative Semantics

**Authoritative (version-controlled):**
- `core/{prd,tsd,adr,kb}/*`
- `extensions/*` (per mesh policy)
- `memory/long_term/*`
- `memory/agent_state/*` (machine-generated state machines, checkpoints)
- `embeddings/index/*` (deterministic indexes, manifests)
- `.sdlc_ide/logs/audit_trail.jsonl`

**Non-Authoritative (excluded from VCS via `.gitignore`):**
- `cache/*`
- `memory/episodic/*`
- `embeddings/vectors/*` (raw binary blobs, or stored in an external Vector DB)
- `.sdlc_ide/logs/*` (excluding `audit_trail.jsonl`)
- `.sdlc_ide/tmp/*`
- `.sdlc_ide/snapshots/*`

**Edge Case:** Derived artifacts (e.g., conflict summaries, impact analyses) are stored in `memory/long_term/` and versioned, because agents need to reason over historical contradictions.

### 2. Episodic vs. Long-Term Memory

**Episodic Memory (non-authoritative, `.gitignore`'d, purged after TTL):**
- Transient observations during an agent's runtime.
- Session-scoped computations and scratch buffers.
- Time-series metrics (QPS, latency).
- **Examples:**
  - `TSD_Check.episodic`: `[{"ts": ..., "status": "in_progress", "duration_ms": ...}]`
  - `Vector_Cache.episodic`: Temporary embeddings during batch computation.

**Long-Term Memory (version-controlled, persistent across restarts):**
- Agent-state machines and checkpoints.
- Contradiction history, drift detection records, and risk profiles.
- Lineage inference history.
- **Examples:**
  - `agent_state/tsd_manager.checkpoint`: `{"last_prd_hash": "abc123", "sync_status": "compliant"}`
  - `memory/contradiction_history.jsonl`: `[{"ts": ..., "prd_id": "PRD-42", "conflict": {...}}]`

### 3. Embedding Storage

The detailed structure and management of embeddings, including the `embeddings/` directory layout, are defined in ADR-003 (Vectorization & Embeddings). This ADR establishes only the high-level separation of version-controlled manifests from non-versioned vector blobs.

### 4. Agent State Machines and Checkpoints

Agent state is persisted to allow for recovery and inspection.

**Example Checkpoint:** `memory/agent_state/tsd_manager.checkpoint.json`
```json
{
  "agent_id": "TSM-001",
  "ts_checkpoint": "2025-11-27T10:15:00Z",
  "last_prd_hash": "abc123def456",
  "last_prd_id": "PRD-42",
  "sync_status": "compliant",
  "sync_log": [
    {"ts": "2025-11-27T10:14:00Z", "status": "check_passed", "drift_score": 0.02}
  ],
  "next_action": "monitor_for_changes"
}
```

### 5. Merge Conflict Resolution

- **Authoritative core documents (`core/*`):**
  - Governor validates both branches before merge.
  - If compliant, use Git's 3-way merge.
  - If merge produces structural conflicts, reject and require manual resolution.
- **Machine-generated logs (`memory/*.jsonl`):**
  - Use append-only semantics (JSONL).
  - Merge by concatenating and deduplicating on `event_id`.
- **Agent checkpoints (`memory/agent_state/*.json`):**
  - Last-write-wins (most recent checkpoint wins).
  - Log the conflict in `logs/merge_conflicts.jsonl` for auditing.
- **Embedding manifests (`embeddings/index/*.json`):**
  - Merge by deduplicating on `artifact_id`.
  - If `model_version` differs, flag for re-embedding.

### 6. Orchestrator Transaction Model

Each agent write is a transaction:
1.  **Acquire Lock**: On `artifact_id` or workspace-wide.
2.  **Stage Writes**: To a temp directory (`.sdlc_ide/tmp/tx-<uuid>/`).
3.  **Validate**: Schemas and governance rules are checked.
4.  **Commit**: Atomic rename to final location (or Git commit).
5.  **Release Lock**:
6.  **Publish Event**: e.g., `File_Written`.

**Write-Ahead Logging (WAL):**
- The Orchestrator maintains `.sdlc_ide/logs/wal.jsonl`.
- Each transaction writes: `{"action": "begin|commit|abort", "tx_id": "...", "files": [...]}`.
- On restart, the Orchestrator replays the WAL to recover incomplete transactions.

### 7. Rollback and Branching Semantics

- **Rollback**:
  - The Governor can trigger a rollback on `core/*` artifacts if a compliance check fails.
  - Rollback creates a new commit (`git revert`), not a history rewrite.
  - An `Artifact_Rolled_Back` event is published.
- **Branching**:
  - Agents can propose branches (e.g., `agent/contradiction-fix`).
  - Agents can write to feature branches.
  - Merging to the main branch requires Governor approval and triggers re-validation of downstream artifacts.

### 8. Event Snapshots and Audit Trail

- **Snapshots**:
  - Created at deterministic points (e.g., TSD validated).
  - Stored in `.sdlc_ide/snapshots/` as `.tar.gz` or as a Git tag.
  - Metadata is stored in a manifest.
- **Audit Trail**:
  - `.sdlc_ide/logs/audit_trail.jsonl` is version-controlled.
  - Records writes, merges, rollbacks, and policy violations.

### 9. Permission Model

Write permissions are enforced by the Governor:
- `core/prd/*`: PRM only (human review required for merge).
- `core/tsd/*`: TSM only (after PRD consistency check).
- `extensions/*`: Governed by extension mesh policy.
- `memory/agent_state/*`: Owning agent only.
- `embeddings/index/*`: Vectorizer agent only.
- `cache/*`, `logs/*`: All agents (append-only for logs).

### 10. PoC Checklist

1.  Create `.sdlc_ide/` directory structure and `.gitignore`.
2.  Initialize a Git repository.
3.  PRM writes a PRD to `core/prd/PRD-001.json`.
4.  Orchestrator commits and publishes `PRD_Written` event.
5.  TSM reads PRD and writes TSD to `core/tsd/TSD-001.json`.
6.  Orchestrator creates a checkpoint: `memory/agent_state/tsm.checkpoint.json`.
7.  A human creates a branch and modifies the PRD.
8.  Governor validates and merges to main.
9.  Verify the audit trail in `logs/audit_trail.jsonl`.

## Dependencies

- **ADR-001 (DAG)**: DAG validation is enforced by the Governor.
- **ADR-002 (Events)**: Events are published on file changes.
- **ADR-003 (Embeddings)**: The embedding manifest and model versioning are defined here.
- **ADR-004 (Orchestrator)**: The transaction model is implemented by the Orchestrator.
- **ADR-009 (Governance and Policy Enforcement)**: Governor/OPA policy definitions are specified in this ADR.

---
## Operational Concerns

- **Disk space**: As the workspace grows, a strategy for archiving old snapshots and pruning old events will be required.
- **Backup/restore**: The primary backup mechanism is the version control system itself (`git push`). However, the state of any external vector database will need to be backed up separately.
- **Multi-tenant**: If SDLC_IDE serves multiple projects, each project will have its own `.sdlc_ide/` workspace to ensure isolation.
