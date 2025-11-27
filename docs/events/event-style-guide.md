# Event Schema Style Guide

This document defines the canonical style and naming conventions for all event schemas in the SDLC_IDE system. Adhering to these conventions is mandatory for all new and updated event schemas to ensure consistency and interoperability.

## Naming Conventions

### Event Property Names

All event property names **MUST** use `camelCase`.

- **Correct:** `commitHash`, `schemaVersion`, `documentId`
- **Incorrect:** `commit_hash`, `schema_version`, `DocumentID`

### Event Type Names

All event type names (the `type` field within the event payload) **MUST** use `PascalCase`.

- **Correct:** `PRD_Updated`, `Agent_Call`, `Policy_Violation`
- **Incorrect:** `prd_updated`, `agentCall`

### Schema File Names

All schema file names **MUST** use the format `<EventType>_v<version>.json`, where `<EventType>` is the `PascalCase` event type.

- **Correct:** `PRD_Updated_v1.json`, `Agent_Call_v1.json`
- **Incorrect:** `prd_updated.v1.json`, `AgentCall_v1.json`

## Schema Structure

All event schemas **MUST** conform to the following structural rules:

1.  **Base Envelope:** All schemas **MUST** inherit from the shared `EventEnvelope_v1.json` using the `allOf` and `$ref` keywords. This ensures that all events contain the required envelope fields (`type`, `schemaVersion`, `ts`, `eventId`, `metadata`).

2.  **Strict Validation:** The event-specific portion of the schema (i.e., the second object in the `allOf` array) **MUST** set `"additionalProperties": false`. This prevents the inclusion of undocumented or non-standard fields in the event payload. The `metadata` field in the envelope remains flexible for unstructured data.

3.  **Documentation:**
    -   Every schema **MUST** have a `description` at the root level explaining the purpose of the event.
    -   Every property **MUST** have a `description` explaining its purpose.

4.  **Examples:** Every schema **MUST** include at least one valid `example` to aid developers in understanding and testing the event structure.
