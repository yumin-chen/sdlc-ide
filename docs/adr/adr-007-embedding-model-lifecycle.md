# ADR-007: Embedding Model Lifecycle

## Status

Proposed

## Context

This ADR defines the lifecycle of embedding models in the system. It covers everything from training and A/B testing to versioning and rollback.

## Decision

The following processes will be used to manage the lifecycle of embedding models:

### Training

Embedding models will be trained on a curated corpus of documents that is representative of the types of documents that will be stored in the system.

### A/B Testing

A/B testing will be used to evaluate the performance of new embedding models. This will involve deploying the new model to a subset of users and comparing its performance to the existing model.

### Corpora

The corpora used for training and evaluating embedding models will be versioned and stored in a dedicated repository.

### Versioning

Embedding models will be versioned using a semantic versioning scheme, and the version will be recorded in the `model_metadata.json` file as defined in ADR-008. This will make it easy to track changes and to roll back to previous versions if necessary.

### Rollback

If a new embedding model is found to be performing poorly, it will be rolled back to the previous version. This will involve updating the `model_metadata.json` file and re-embedding all affected artifacts. The process will be managed through the embedding manifests defined in ADR-008.

## Consequences

By defining a clear lifecycle for embedding models, we can ensure that the system is using the best possible models and that we can respond quickly to any issues that may arise.
