# SDLC_IDE: A Multi-Agent System for Software Development Lifecycle Management

## 1. Overview

SDLC_IDE is a multi-agent system designed to manage all document artifacts throughout the software development lifecycle. It provides a robust and flexible framework for defining, managing, and governing the relationships between different documents, ensuring a deterministic and auditable development process.

The system is built on a **Hybrid Directed Graph Architecture** that combines a strict, core workflow with flexible, user-defined extensions. This allows for both strong governance and adaptability, making it suitable for a wide range of development methodologies.

## 2. Architecture

The architecture of SDLC_IDE is composed of three main components:

*   **Core Directed Acyclic Graph (DAG):** Defines the strict, deterministic workflow for core SDLC documents, ensuring that they follow a predefined lifecycle.
*   **Selective Mesh Extension Layer:** Allows for the integration of user-defined document types and relationships, providing flexibility and extensibility.
*   **Event-Based Observer Layer:** Captures and analyzes events throughout the system, providing insights and enabling AI-driven assistance.

```mermaid
graph TD
    subgraph CoreDAG ["Core DAG (Strict SDLC Flow)"]
        direction TB
        PRD[PRD Manager] -->|Flows Into| TSD[TSD Manager]
        TSD -->|Triggers| ADR[ADR Manager]
        ADR -->|Archives To| KB[KB Manager]
    end

    subgraph Mesh ["Mesh Extensions (Flexible)"]
        direction TB
        Comp[Compliance Module]
        API[API Spec]
        Perf[Performance Model]
    end

    subgraph Gov ["Governance & Observation"]
        Orch[Orchestrator]
        Events[Event Layer]
    end

    %% Mesh relationships
    TSD -.->|References| API
    TSD -.->|References| Perf
    PRD -.->|Validates against| Comp

    %% Orchestrator Control
    Orch -.-|Governs| PRD
    Orch -.-|Governs| TSD
    Orch -.-|Governs| ADR
    Orch -.-|Governs| KB
    Orch -.-|Validates ACL| Comp

    %% Event Layer
    PRD -.-|Emits Events| Events
    TSD -.-|Emits Events| Events
    ADR -.-|Emits Events| Events
    KB -.-|Emits Events| Events
    Comp -.-|Emits Events| Events
```

## 3. Governance

The SDLC_IDE project uses a governance model based on the **Open Policy Agent (OPA)** to enforce architectural constraints and ensure that all changes to the system are made in a controlled and deliberate manner.

### Architecture Decision Records (ADRs)

All significant architectural decisions are documented in **Architecture Decision Records (ADRs)**, which are stored in the `docs/architecture/design` directory. ADRs follow a strict naming convention to ensure consistency: `adr-XXX-kebab-case-description.md`, where `XXX` is the ADR number.

ADRs are subject to a strict approval process, enforced by an OPA policy, which requires that they be submitted via a pull request and reviewed by the project maintainers.

### OPA Policy

The OPA policy, defined in `docs/governance/policies/adr_policy.rego`, ensures that all changes to ADRs are made through a pull request. This allows for a thorough review and discussion of all proposed changes, ensuring that they are in line with the project's architectural principles.

## 4. Getting Started

To get started with the SDLC_IDE project, you will need to have the following tools installed:

*   **OPA:** The Open Policy Agent is used to enforce the project's governance policies.
*   **Conftest:** A utility for testing your configuration files using OPA.

Once you have these tools installed, you can run the policy checks locally using the following command:

```bash
conftest test docs/adr/ --policy docs/governance/policies/adr_policy.rego --namespace sdlc.governance
```

## 5. Contributing

We welcome contributions to the SDLC_IDE project. If you would like to contribute, please follow these guidelines:

*   All significant architectural changes must be documented in an ADR.
*   ADRs must be submitted via a pull request and reviewed by the project maintainers.
*   All code contributions must be accompanied by appropriate tests.

By following these guidelines, you can help us to ensure that the SDLC_IDE project remains a robust and reliable platform for managing the software development lifecycle.
