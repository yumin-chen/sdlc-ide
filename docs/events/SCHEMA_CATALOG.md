# Event Schema Catalog

This document provides a catalog of all event schemas, automatically generated from the JSON schema files.

## Common Envelope Properties (`EventEnvelope.v1`)

All events share this common set of base properties.

| Property | Type | Description | Required |
|---|---|---|---|
| **`type`** | `string` | Type of the event | Yes |
| **`schemaVersion`** | `string` | Version of the schema | Yes |
| **`ts`** | `string` | Timestamp of the event | Yes |
| **`eventId`** | `ref (`#/$defs/uuid`)` | Unique event identifier | Yes |
| **`traceId`** | `ref (`#/$defs/uuid`)` | Correlation ID for tracing the flow across agents | No |
| **`eventSource`** | `string` | Subsystem or service that produced this event | No |
| **`metadata`** | `object` | Flexible metadata field | No |

---
## TSD_Updated.v1

**Description:** Event emitted when a Technical Specification Document (TSD) is updated.

**Schema File:** [`TSD_Updated_v1.json`](./schema-registry/TSD_Updated_v1.json)

### Event-Specific Properties

| Property | Type | Description | Required |
|---|---|---|---|
| **`type`** | `const (`TSD_Updated`)` | null | No |
| **`schemaVersion`** | `const (`v1`)` | null | No |
| **`tsdId`** | `string` | Technical Specification Document identifier | Yes |
| **`artifactPaths`** | `array` | Paths to the artifacts | No |
| **`canonicalHash`** | `string` | Canonical hash of the document | No |
| **`changeSummary`** | `string` | Summary of changes made | No |

### Example

```json
{
  "type": "TSD_Updated",
  "schemaVersion": "v1",
  "ts": "2025-11-27T10:30:00Z",
  "eventId": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "tsdId": "TSD-042",
  "artifactPaths": [
    "openapi/v1/payments.json"
  ],
  "canonicalHash": "...",
  "changeSummary": "added endpoint /authorize"
}

```

---
## Policy_Violation.v1

**Description:** Event emitted when a policy violation occurs.

**Schema File:** [`Policy_Violation_v1.json`](./schema-registry/Policy_Violation_v1.json)

### Event-Specific Properties

| Property | Type | Description | Required |
|---|---|---|---|
| **`type`** | `const (`Policy_Violation`)` | null | No |
| **`schemaVersion`** | `const (`v1`)` | null | No |
| **`policyId`** | `string` | Policy identifier | Yes |
| **`violationDetails`** | `string` | Details of the violation | Yes |
| **`actor`** | `string` | Actor responsible for the violation | Yes |
| **`documentId`** | `string` | Document identifier | No |

### Example

```json
{
  "type": "Policy_Violation",
  "schemaVersion": "v1",
  "ts": "2025-11-27T10:30:00Z",
  "eventId": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "policyId": "policy-001",
  "violationDetails": "Unauthorized access attempt to PRD-007",
  "actor": "user-123",
  "documentId": "PRD-007"
}

```

---
## Git_Commit.v1

**Description:** Event emitted when a commit is made to the repository.

**Schema File:** [`Git_Commit_v1.json`](./schema-registry/Git_Commit_v1.json)

### Event-Specific Properties

| Property | Type | Description | Required |
|---|---|---|---|
| **`type`** | `const (`Git_Commit`)` | null | No |
| **`schemaVersion`** | `const (`v1`)` | null | No |
| **`commitHash`** | `string` | Commit hash | Yes |
| **`author`** | `string` | Author of the commit | Yes |
| **`message`** | `string` | Commit message | Yes |
| **`filesChanged`** | `array` | List of files changed | No |

### Example

```json
{
  "type": "Git_Commit",
  "schemaVersion": "v1",
  "ts": "2025-11-27T12:00:00Z",
  "eventId": "3e0c5dbf-5fac-4f2c-9ea4-4c2db0ec1fee",
  "commitHash": "a1c9f...",
  "author": "yumin731598",
  "message": "Updated PRD for new API endpoint",
  "filesChanged": [
    "docs/prd/prd-042.md"
  ]
}

```

---
## Agent_Call.v1

**Description:** Event emitted when an agent makes a call to another agent.

**Schema File:** [`Agent_Call_v1.json`](./schema-registry/Agent_Call_v1.json)

### Event-Specific Properties

| Property | Type | Description | Required |
|---|---|---|---|
| **`type`** | `const (`Agent_Call`)` | null | No |
| **`schemaVersion`** | `const (`v1`)` | null | No |
| **`from`** | `string` | Source agent | Yes |
| **`to`** | `string` | Destination agent | Yes |
| **`action`** | `string` | Action performed | Yes |
| **`callTrace`** | `string` | Trace identifier for the call | Yes |
| **`status`** | `string enum (`enqueued`, `success`, `failed`)` | Status of the call | Yes |

### Example

```json
{
  "type": "Agent_Call",
  "schemaVersion": "v1",
  "ts": "2025-11-27T10:30:00Z",
  "eventId": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "from": "PRM",
  "to": "TSM",
  "action": "request-tsd-check",
  "callTrace": "trace-xxx",
  "status": "enqueued"
}

```

---
## Artifact_Vectorized.v1

**Description:** Event emitted when an artifact is vectorized.

**Schema File:** [`Artifact_Vectorized_v1.json`](./schema-registry/Artifact_Vectorized_v1.json)

### Event-Specific Properties

| Property | Type | Description | Required |
|---|---|---|---|
| **`type`** | `const (`Artifact_Vectorized`)` | null | No |
| **`schemaVersion`** | `const (`v1`)` | null | No |
| **`artifactId`** | `string` | Artifact identifier | Yes |
| **`vectorId`** | `string` | Vector identifier | Yes |

### Example

```json
{
  "type": "Artifact_Vectorized",
  "schemaVersion": "v1",
  "ts": "2025-11-27T10:30:00Z",
  "eventId": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "artifactId": "openapi/...#endpoint/authorize",
  "vectorId": "vec-9876",
  "metadata": {
    "component": "payments",
    "commit": "a1c9f..."
  }
}

```

---
## User_Interaction.v1

**Description:** Event emitted when a user interacts with a document.

**Schema File:** [`User_Interaction_v1.json`](./schema-registry/User_Interaction_v1.json)

### Event-Specific Properties

| Property | Type | Description | Required |
|---|---|---|---|
| **`type`** | `const (`User_Interaction`)` | null | No |
| **`schemaVersion`** | `const (`v1`)` | null | No |
| **`user`** | `string` | User performing the action | Yes |
| **`action`** | `string enum (`view`, `edit`, `comment`)` | Action performed by the user | Yes |
| **`documentId`** | `string` | Document identifier | Yes |

### Example

```json
{
  "type": "User_Interaction",
  "schemaVersion": "v1",
  "ts": "2025-11-27T10:30:00Z",
  "eventId": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "user": "yumin731598",
  "action": "view",
  "documentId": "PRD-042"
}

```

---
## PRD_Updated.v1

**Description:** Event emitted when a Product Requirement Document (PRD) is updated.

**Schema File:** [`PRD_Updated_v1.json`](./schema-registry/PRD_Updated_v1.json)

### Event-Specific Properties

| Property | Type | Description | Required |
|---|---|---|---|
| **`type`** | `const (`PRD_Updated`)` | null | No |
| **`schemaVersion`** | `const (`v1`)` | null | No |
| **`project`** | `string` | Project identifier | Yes |
| **`prdId`** | `string` | Product Requirements Document identifier | Yes |
| **`author`** | `string` | Author of the update | Yes |
| **`commitHash`** | `string` | Commit hash for the update | No |
| **`deltaHash`** | `string` | Hash representing the changes made | No |
| **`requiredChecks`** | `array` | List of required checks | No |

### Example

```json
{
  "type": "PRD_Updated",
  "schemaVersion": "v1",
  "ts": "2025-11-27T10:30:00Z",
  "eventId": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "project": "project-phi",
  "prdId": "PRD-042",
  "author": "yumin731598",
  "commitHash": "a1c9f...",
  "deltaHash": "d3f9e...",
  "requiredChecks": [
    "tsd_sync"
  ],
  "metadata": {
    "visibility": "internal",
    "sensitivity": "low"
  }
}

```
