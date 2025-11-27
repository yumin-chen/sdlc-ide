# SDLC_IDE: A Multi-Agent System for Software Development Lifecycle Management

## Table of Contents

1.  [Overview](#1-overview)
2.  [Architecture (Revised for Terminology Clarity)](#2-architecture-revised-for-terminology-clarity)
3.  [Key Principles](#3-key-principles)
4.  [Governance (Revised for Policy Detail)](#4-governance-revised-for-policy-detail)
    *   [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs)
    *   [OPA Policy](#opa-policy)
5.  [Getting Started](#5-getting-started)
6.  [Contributing](#6-contributing)

## 1. Overview

SDLC_IDE is a multi-agent system designed to manage all document artifacts throughout the software development lifecycle. It provides a robust and flexible framework for defining, managing, and governing the relationships between different documents, ensuring a deterministic and auditable development process.

The system is built on a **Hybrid Directed Graph Architecture** that combines a strict, core workflow with flexible, user-defined extensions. This allows for both strong governance and adaptability, making it suitable for a wide range of development methodologies.

## 2. Architecture (Revised for Terminology Clarity)

The architecture of SDLC_IDE is composed of three main components:

  * **Core Directed Acyclic Graph (DAG):** Defines the strict, deterministic workflow for core SDLC documents, ensuring they follow a predefined lifecycle. This graph manages the transition between primary artifacts like the **Product Requirements Document (PRD)**, **Technical Specification Document (TSD)**, and **Architecture Decision Records (ADRs)**.
  * **Selective Mesh Extension Layer:** Allows for the integration of user-defined document types and relationships, providing flexibility and extensibility (e.g., Compliance Policies, API Specifications).
  * **Event-Based Observer Layer:** Captures and analyzes all status and relationship events throughout the system. This layer provides crucial **insights and enables AI-driven assistance**, such as proactively suggesting relevant API specs when a TSD is being drafted, or flagging potential compliance violations.

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

## 3. Key Principles

The SDLC_IDE project is guided by a set of key architectural principles that ensure a clear separation of concerns and a robust, scalable system.

*   **Human-Governed Core:** The Core DAG is considered immutable to autonomous agents. Any modifications to the core flow require explicit human approval via the Architecture Decision Record (ADR) governance process. This ensures that the primary SDLC lifecycle remains stable and predictable.
*   **Agent-Driven Extensibility:** The Mesh Extension Layer is designed for dynamic, autonomous extensions. Agents can propose and manage their own document types and relationships within this layer, allowing for flexible and adaptable workflows.
*   **Single Source of Authority (SSoA):** The Core DAG serves as the single source of truth for the SDLC lifecycle. The Mesh can enrich and extend the core, but it can never override its fundamental structure. This ensures a clear and consistent understanding of the development process.
*   **Separation of Concerns:** The architecture enforces a strict separation between the Core DAG and the Mesh extensions. This allows for independent development and evolution of each component, reducing the risk of unintended side effects.

## 4. Governance (Revised for Policy Detail)

The SDLC_IDE project uses a governance model based on the **Open Policy Agent (OPA)** to enforce architectural constraints and ensure that all changes to the system are made in a controlled and deliberate manner.

### Architecture Decision Records (ADRs)

All significant architectural decisions are documented in **Architecture Decision Records (ADRs)**, which are stored in the `docs/architecture/design` directory. ADRs follow a strict naming convention to ensure consistency: `adr-XXX-kebab-case-description.md`, where `XXX` is the ADR number.

ADRs are subject to a strict approval process, enforced by an OPA policy, which requires that they be submitted via a pull request and reviewed by the project maintainers.

### OPA Policy

The OPA policy, defined in `docs/governance/policies/adr_policy.rego`, ensures strict adherence to governance principles. The policy enforces rules such as:

  * All ADR file changes must originate from a pull request.
  * The ADR number (`XXX`) must be unique and strictly sequential within the directory.
  * The title of the ADR must adhere to defined formatting constraints.

This rigorous checking allows for a thorough review and discussion of all proposed changes, ensuring they are in line with the project's architectural principles.

## 5. Getting Started

This section will guide you through the process of setting up your local environment and running the project's governance checks.

### Prerequisites

Before you begin, you will need to have the following tools installed:

*   **Open Policy Agent (OPA):** A lightweight, general-purpose policy engine. You can download it from the [official OPA website](https://www.openpolicyagent.org/docs/latest/#running-opa).
*   **Conftest:** A utility that helps you write tests against structured configuration data. You can install it by following the instructions in the [Conftest documentation](https://www.conftest.dev/install/).

### Installation

1.  **Install OPA:**

    Follow the installation instructions on the [OPA website](https://www.openpolicyagent.org/docs/latest/#running-opa) to download and install the OPA binary for your operating system.

2.  **Install Conftest:**

    Follow the installation instructions in the [Conftest documentation](https://www.conftest.dev/install/) to install Conftest on your system.

### Running the Governance Checks

Once you have installed OPA and Conftest, you can run the governance checks locally to ensure that all ADRs comply with the project's policies.

The following command will execute the OPA policy against all ADRs in the `docs/adr` directory:

```bash
conftest test docs/adr/ --policy docs/governance/policies/adr_policy.rego --namespace sdlc.governance
```

If all the checks pass, you will see a confirmation message in your terminal. If any of the checks fail, you will see a detailed report of the violations.

## 6. Contributing

We welcome contributions to the SDLC_IDE project. Whether you're interested in fixing bugs, adding new features, or improving the documentation, your help is greatly appreciated.

To ensure a smooth and collaborative process, please follow these guidelines:

### Submitting an ADR

For any significant architectural changes, you must submit an Architecture Decision Record (ADR) before you start writing any code. This allows the project maintainers to review your proposal and provide feedback before you invest a significant amount of time in implementation.

When submitting an ADR, please:

*   Follow the naming convention: `adr-XXX-kebab-case-description.md`.
*   Use the ADR template in `docs/architecture/templates/adr-template.md`.
*   Clearly describe the proposed changes and the problem they are intended to solve.
*   Submit the ADR as a pull request to the `main` branch.

### Submitting a Pull Request

For all code contributions, please submit a pull request with the following:

*   A clear and concise title and description of the changes.
*   A link to the relevant ADR, if applicable.
*   A summary of the tests you have added or updated.

By following these guidelines, you can help us to ensure that the SDLC_IDE project remains a robust and reliable platform for managing the software development lifecycle. We look forward to your contributions!
