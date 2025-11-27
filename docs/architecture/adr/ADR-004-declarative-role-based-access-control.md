# ADR-004: Declarative Role-Based Access Control (RBAC)

*   **Status:** Proposed
*   **Date:** 2024-05-14
*   **Deciders:** Jules (AI Agent)

## Context and Problem Statement

The SDLC_IDE system requires a formal, declarative, and auditable permission model. While the README mentions using a policy engine (OPA), the specific roles, the agents they map to, and the data attributes needed for policy decisions have not been defined. This ADR specifies the foundational model for Role-Based Access Control (RBAC).

## Decision Drivers

*   **Declarative Permissions:** Permissions must be defined in a human-readable, machine-enforceable format.
*   **Deterministic Enforcement:** The policy engine must be deterministic, producing the same result for the same input.
*   **Separation of Policy and Code:** Policy logic should be decoupled from the application code.
*   **Auditability:** All permission decisions must be auditable, requiring clear provenance and ownership data.

## Considered Options

1.  **Ad-hoc Permissions:** Define permissions directly within the code of each agent. This is not declarative, hard to audit, and tightly coupled.
2.  **Centralized RBAC Model:** Define a formal, centralized set of roles and attributes enforced by a dedicated policy engine. This aligns with the existing decision to use OPA.

## Decision Outcome

We will adopt a centralized RBAC model enforced by OPA. This model will be based on a canonical role list, a mapping of those roles to system agents, and a minimal set of security attributes attached to every request.

### Canonical Role List

The system will define the following canonical roles:

| Role                 | Description                                                                       |
| -------------------- | --------------------------------------------------------------------------------- |
| `CoreContributor`    | Can author and modify artifacts within the Core DAG (e.g., PRDs, TSDs, ADRs).     |
| `ExtensionDeveloper` | Can create, manage, and register new templates and extensions in the Mesh Layer.  |
| `SystemObserver`     | Has read-only access to all artifacts for the purpose of observation and analysis. |

### Agent to Role Mapping

The existing system agents will be mapped to these roles as follows:

| Agent                 | Role                 | Justification                                                                 |
| --------------------- | -------------------- | ----------------------------------------------------------------------------- |
| `PRD Manager`         | `CoreContributor`    | Manages a core SDLC artifact.                                                 |
| `TSD Manager`         | `CoreContributor`    | Manages a core SDLC artifact.                                                 |
| `ADR Manager`         | `CoreContributor`    | Manages a core SDLC artifact.                                                 |
| `KB Manager`          | `SystemObserver`     | Primarily archives and indexes information, requiring read-access.            |
| Custom Mesh Agents    | `ExtensionDeveloper` | These agents are responsible for extending the system with custom artifacts.   |

### Minimal Attribute Set

Every request subject to a policy check MUST include the following attributes:

| Attribute      | Type     | Description                                                                           | Example                               |
| -------------- | -------- | ------------------------------------------------------------------------------------- | ------------------------------------- |
| `risk_score`   | Integer  | A numerical score (0-100) indicating the potential risk of the action.                  | `75`                                  |
| `provenance`   | String   | A URI identifying the origin of the request.                                          | `git://my-repo/commit/abc123`         |
| `environment`  | String   | The target environment for the action.                                                | `dev`, `staging`, `prod`              |
| `owner`        | String   | The identity of the principal (human or agent) initiating the action.                 | `user:jane.doe`, `agent:PRDManager` |
