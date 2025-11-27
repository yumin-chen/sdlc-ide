# ADR-003: Vectorization & Embeddings

## Status

Proposed

## Context

This ADR defines the strategy for vectorizing and managing embeddings for all artifacts in the system. Embeddings are crucial for enabling semantic search, drift detection, and other AI-powered features.

## Decision

The system will employ a multi-faceted approach to vectorization, including structural and semantic embeddings, lazy embedding, and a robust model versioning strategy.

### 1. Structural Embeddings

To capture the structural essence of artifacts, we will use the following strategies:

-   **PRD Structure:** A PRD's structure will be represented as a JSON schema, which is then treated as a tree for structural embedding.
-   **TSD Structure:** A TSD's structure will be serialized from its OpenAPI AST (Abstract Syntax Tree). Section-level embeddings will be derived from the AST nodes.

### 2. Model Versioning and Re-embedding Strategy

The system will support two modes for handling model version updates:

-   **(A) Freeze Old Embeddings (Default):** Older artifacts will retain their existing embeddings to ensure stability.
-   **(B) Re-embed All Artifacts:** This mode, triggered by an operator or the orchestrator, will re-embed all artifacts with the new model.

The vector database will store a `model_version` field with each embedding to facilitate this process.

### 3. Fragment-Level Embeddings and Cost Management

To manage the computational cost of embeddings, the following strategies will be used:

-   **Lazy Embedding:** Embeddings will be generated on-demand when an artifact is accessed or modified.
-   **Caching:** A caching layer will store frequently accessed embeddings to reduce redundant computations.
-   **Scheduled Re-embedding:** A scheduled process will re-embed artifacts that have been recently edited.

### 4. Drift Detection and Conflict Detection

Embeddings will be used to enable drift detection, but the decision logic will reside in the Orchestrator (ADR-005) and specialized agents (e.g., `ContradictionDetector`).

### 5. Custom Document Type Integration

To join the mesh, a custom document type must:
- Declare a schema.
- Declare lineage edges.
- Define an embedding strategy.
- Pass orchestrator validation (as defined in ADR-005).

Further details on this process are available in ADR-006.

### 6. Embedding Storage

As defined in ADR-004, embeddings are split into version-controlled manifests and non-versioned vectors.

```
embeddings/
  index/  (Version-Controlled)
    model_metadata.json:
      {
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "model_version": "v2.1",
        "ts_generated": "2025-11-27T10:00:00Z",
        "commit_hash": "abc123"
      }
    artifact_vectors.manifest.json:
      {
        "artifacts": [
          {"artifact_id": "PRD-42", "vec_id": "vec-abc123", "granularity": "document"},
          {"artifact_id": "PRD-42#section-goals", "vec_id": "vec-def456", "granularity": "section"}
        ]
      }
  vectors/ (Not Version-Controlled)
    [Stored externally or as binary blobs]
```

## Consequences

This approach will provide a robust and scalable solution for managing embeddings, enabling a wide range of AI-powered features while managing costs and complexity.
