# SDLC_IDE: A Multi-Agent System for Software Development Lifecycle Management

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Key Principles](#3-key-principles)
4. [Governance](#4-governance)
    * [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs)
    * [OPA Policy](#opa-policy)
5. [Getting Started](#5-getting-started)
6. [Contributing](#6-contributing)

---

## 1. Overview

SDLC_IDE is a multi-agent system for managing all document artifacts throughout the **Software Development Lifecycle (SDLC)**. It provides a predictable, auditable, and extensible workflow through a **Hybrid Directed Graph Architecture** that combines:

* A strict, compliance-friendly **Core SDLC DAG**, and
* A flexible, user-defined **Mesh Extension Layer**.

This hybrid design ensures **strong governance and deterministic lifecycle flow**, while enabling teams to define additional document types, relationships, and semantics without compromising core integrity.

---

## 2. Architecture

The system architecture is organized into **three primary layers**:

### Core Directed Acyclic Graph (DAG)

Defines the authoritative SDLC workflow: `PRD → TSD → ADR → KB` (Product Requirements Document, Technical Specification Document, Architecture Decision Record, Knowledge Base).

**Properties:**

* Deterministic and acyclic flow
* Strong communication boundaries
* Fully governed by the Orchestrator
* No lateral propagation or gossip between core managers
* Fully auditable lifecycle transitions

### Selective Mesh Extension Layer

A flexible layer for user-defined document types (e.g., API Specs, Compliance Policies, Performance Models).

**Characteristics:**

* Declarative schemas and allowed edges
* **Cannot modify or override the Core DAG**
* May include local communication inside Mesh clusters
* Semantic links permitted (via embeddings) but never structural
* Safely validated by Orchestrator + Governor

### Event-Based Observer Layer

Captures system activity for analytics and ML-driven assistance.

**The Event Layer:**

* Emits immutable lifecycle and communication events
* Provides insights, predictions, and recommendations (e.g., suggesting relevant API specs)
* Does **not** influence graph structure

### Architecture Diagram

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
````

-----

## 3\. Key Principles

The SDLC_IDE project is guided by a set of key architectural principles that ensure a clear separation of concerns and a robust, scalable system.

  * **Human-Governed Core:** The Core DAG is immutable to autonomous agents. Any modification requires human review via the ADR process. This ensures the primary SDLC lifecycle remains stable and predictable.
  * **Agent-Driven Extensibility:** Agents may propose new Mesh document types, relationships, and behaviors—validated by the Orchestrator + Governor.
  * **Single Source of Authority (SSoA):** The Core DAG is authoritative and cannot be altered or bypassed by extensions.
  * **Strong Separation of Concerns:** Core and Mesh layers evolve independently under strict boundaries, reducing risk and unintended side effects.

-----

## 4\. Governance

SDLC_IDE uses **Open Policy Agent (OPA)** to enforce structural and process governance, ensuring all architectural changes are controlled and deliberate.

### Architecture Decision Records (ADRs)

All major architectural decisions are documented in ADRs under:

```
docs/architecture/design/
```

**Conventions:**

  * **Filename:** `adr-XXX-kebab-case-description.md`
  * **XXX** is strictly sequential starting from `000`
  * All ADRs require review via a pull request

### OPA Policy

The policy defined in:

```
docs/governance/policies/adr_policy.rego
```

**enforces constraints such as:**

  * ADR changes must originate from a Pull Request.
  * ADR numbering must be sequential with no gaps.
  * Title formatting must follow project standards.

OPA ensures consistency, compliance, and traceability of architectural evolution.

-----

## 5\. Getting Started

This section guides you through setting up your local environment to validate governance checks.

### Prerequisites

Before you begin, you will need the following tools installed. These tools are required to **test our governance rules locally** against your ADR configuration files *before* submitting them.

  * **Open Policy Agent (OPA):** A lightweight, general-purpose policy engine. You can download it from the [official OPA website](https://www.openpolicyagent.org/docs/latest/#running-opa).
  * **Conftest:** A utility that helps you write tests against structured configuration data. We use it to execute the OPA policies against your documents. You can install it by following the instructions in the [Conftest documentation](https://www.conftest.dev/install/).

### Installation

1.  **Install OPA:** Follow the instructions on the [OPA website](https://www.openpolicyagent.org/docs/latest/#running-opa).
2.  **Install Conftest:** Follow the instructions in the [Conftest documentation](https://www.conftest.dev/install/).

### Running Governance Checks

Once installed, run the following command to execute the OPA policy against all ADRs in the `docs/adr` directory:

```bash
conftest test docs/adr/ --policy docs/governance/policies/adr_policy.rego --namespace sdlc.governance
```

You will receive detailed pass/fail reports for all ADRs.

-----

## 6\. Contributing

We welcome contributions to the SDLC_IDE project.

### Proposing Architecture Changes

For any significant architectural changes, submit an ADR before writing code. This allows for maintainer review and feedback.

When submitting an ADR, please:

  * Follow the naming convention: `adr-XXX-kebab-case-description.md`.
  * Use the template in `docs/architecture/templates/adr-template.md`.
  * Submit via a Pull Request and provide clear rationale, impact, and alternatives.

### Submitting Code Changes

For all code contributions, submit a pull request with the following:

  * A clear and concise title and description.
  * A link to the relevant ADR, if applicable.
  * A summary of the tests you have added or updated.

By following these guidelines, you help us ensure that the SDLC_IDE project remains a robust and reliable platform.
