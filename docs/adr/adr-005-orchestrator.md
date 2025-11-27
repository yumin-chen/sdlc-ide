# ADR-005: Orchestrator Architecture

## Status

Proposed

## Context

This ADR defines the architecture of the Orchestrator, a central component responsible for maintaining the integrity of the DAG and mesh, validating changes, and coordinating the activities of other agents.

## Decision

The Orchestrator will be implemented as a state machine that processes change requests and emits events. It will be responsible for the following:

### State Machine

The Orchestrator will maintain a state machine for each artifact, tracking its lifecycle from creation to archival.

### Cycle Detection Rules

The Orchestrator will implement cycle detection algorithms to prevent circular dependencies in the DAG.

### Mesh Validation Rules

The Orchestrator will enforce validation rules for mesh edges, ensuring that custom document types are integrated correctly.

### Event Consumption

The Orchestrator will consume events from the event streaming layer for auditing and to trigger validation processes. It will not act exclusively on events, but will use them to supplement its decision-making process.

### Decision Making

The Orchestrator will delegate decisions about semantic drift and contradictions to specialized agents, but will be responsible for initiating these checks and acting on their results. A concrete example of such an agent is the `ContradictionDetector`, the design of which is specified in `docs/agents/contradiction-detector.md`.

### Transaction Model

As defined in ADR-004, the Orchestrator will manage all write operations as transactions, ensuring atomicity and durability. This includes acquiring locks, staging writes, validating changes, and using a write-ahead log (WAL) for recovery.

### Agent State Management

The Orchestrator will be responsible for managing agent state, including checkpoints and history. This will allow for agents to be stateless and for their operations to be replayable.

### Merge Conflict Resolution

The Orchestrator will enforce the merge conflict resolution policies defined in ADR-004. This includes using different strategies for different types of artifacts, such as 3-way merges for core documents and last-write-wins for agent checkpoints.

### Rollback Semantics

The Orchestrator will implement the rollback semantics defined in ADR-004. This includes creating new commits for rollbacks (rather than rewriting history) and publishing `Artifact_Rolled_Back` events.

## Consequences

The Orchestrator will be a critical component for maintaining the integrity of the system. Its performance and reliability will be key to the overall success of the project. By centralizing these critical functions, we can ensure that the system is consistent, resilient, and auditable.
