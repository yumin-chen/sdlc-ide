# ADR-006: Failure Modes & Degradation

## Status

Proposed

## Context

This ADR documents the expected behavior of the system in the face of various failure modes. It describes how the system will degrade gracefully and what fallback mechanisms will be in place.

## Decision

The following failure modes and degradation strategies have been identified:

### Event Streaming Down

If the event streaming layer is down, changes to the DAG will be either blocked or cached, depending on the configuration. This will prevent the system from entering an inconsistent state.

### Vector DB Down

If the vector database is down, semantic agents will degrade gracefully. They will still be able to function based on structural information, but their ability to detect semantic drift and contradictions will be limited.

### Embedding Model Version Upgrades

When a new version of an embedding model is released, a reindexing strategy will be triggered. This will involve re-embedding all affected artifacts and updating the vector database. The process will be managed through the embedding manifests defined in ADR-008. During this time, the system will continue to function using the old embeddings, but will gradually switch over to the new embeddings as they become available.

## Consequences

By documenting the expected behavior of the system in the face of failure, we can ensure that the system is resilient and that users are not surprised by its behavior.
