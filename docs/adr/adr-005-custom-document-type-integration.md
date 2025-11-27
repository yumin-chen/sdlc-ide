# ADR-005: Custom Document Type Integration

## Status

Proposed

## Context

This ADR defines the process for integrating custom document types into the system. It outlines the requirements that custom document types must meet to be considered valid and to be able to participate in the DAG and mesh.

## Decision

To integrate a custom document type, the following requirements must be met:

### Schema Definition

A JSON schema must be provided for the custom document type. This schema will be used for validation and to drive the UI.

### ACL

Access control lists (ACLs) must be defined for the custom document type, specifying who can create, read, update, and delete instances of the document type.

### Embedding Requirements

An embedding strategy must be defined for the custom document type. This includes specifying which fields should be embedded and which model should be used.

### Lineage Requirements

The lineage requirements for the custom document type must be specified. This includes defining how the document type relates to other document types in the DAG and mesh.

### Integration Tests

Integration tests must be provided for the custom document type. These tests should cover all aspects of the document type's lifecycle, from creation to archival.

### Attachment to DAG and Mesh

The process for attaching custom documents to the DAG and mesh must be defined. This includes specifying the types of edges that can be created and the validation rules that apply.

## Consequences

By defining a clear process for integrating custom document types, we can ensure that the system remains consistent and that all document types are treated as first-class citizens.
