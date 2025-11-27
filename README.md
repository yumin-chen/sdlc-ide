
# SDLC_IDE — Multi-Agent System for Software Development Lifecycle Management

A governance-first, extensible multi-agent SDLC framework that combines deterministic core workflow control with flexible, policy-validated extensions.
SDLC_IDE ensures architectural integrity, systematic decision-making, and safe agent-driven automation.

---

# Table of Contents

* [Quick Start](#quick-start)
* [Architecture Overview](#architecture-overview)
* [Key Principles](#key-principles)
* [Governance & Compliance](#governance--compliance)
* [Contributing](#contributing)
* [Repository Structure](#repository-structure)
* [Practical Examples](#practical-examples)
* [Deployment](#deployment)
* [Troubleshooting](#troubleshooting)
* [Support & License](#support--license)

---

# Quick Start

## Prerequisites

* Go 1.21+
* Docker & Docker Compose
* Open Policy Agent (OPA)
* Conftest
* Helm 3.0+

## Installation

```bash
# Clone repository
git clone https://github.com/Chen-Software/sdlc-ide.git
cd sdlc-ide

# Install OPA
curl -L https://openpolicyagent.org/downloads/latest/opa_linux_x86_64 -o opa
chmod +x opa

# Install Conftest
curl -L https://github.com/open-policy-agent/conftest/releases/download/v0.46.0/conftest_0.46.0_Linux_x86_64.tar.gz -o conftest.tar.gz
tar xf conftest.tar.gz

# Validate governance policies locally
./conftest test docs/architecture/design/ \
  --policy docs/governance/policies/adr_policy.rego \
  --namespace sdlc.governance

# Run tests
go test -v ./...

# Run local system
docker-compose up -d
```

---

# Architecture Overview

SDLC_IDE consists of three tightly integrated layers, balancing strict governance with controlled extensibility.

---

## 1. Core Directed Acyclic Graph (DAG)

The canonical, immutable SDLC workflow:

**PRD → TSD → ADR → KB**

### Types

| Type | Description                      |
| ---- | -------------------------------- |
| PRD  | Product Requirements Document    |
| TSD  | Technical Specification Document |
| ADR  | Architecture Decision Record     |
| KB   | Knowledge Base Archive           |

### Properties

* Deterministic, rule-based transitions
* Human-governed changes via PRs
* Orchestrator-enforced lifecycle
* Fully auditable event trail
* Agents cannot modify Core DAG

---

## 2. Selective Mesh Extension Layer

A controlled, policy-validated mechanism for adding custom document types, semantic links, or implementation artifacts.

### Supported Examples

* API Specifications
* Compliance Reports
* Performance Models
* Project-specific artifacts

### Constraints

* Declarative schema with `allowed_edges`
* Cannot override Core DAG rules
* Validated by Orchestrator + OPA Governor
* Supports semantic embeddings and local agent collaboration

---

## 3. Event-Based Observer Layer

Immutable event stream for system introspection and agent reactions.

### Capabilities

* Lifecycle event emission
* Agent analytics and ML predictions
* High-integrity audit logs
* Downstream observer consumption

**Note:** The Event Layer never mutates the Core DAG.

---

# Key Principles

## Human-Governed Core

All Core DAG modifications require an ADR and human PR approval.

## Agent-Driven Extensibility

Agents may propose Mesh extensions, subject to policy validation.

## Single Source of Authority (SSoA)

The Core DAG is canonical. Mesh layers extend but do not override.

## Strict Separation of Concerns

Core and Mesh evolve independently under enforced boundaries.

---

# Governance & Compliance

## Architecture Decision Records (ADRs)

* **Location:** `docs/architecture/design/`
* **Naming:** `adr-XXX-kebab-case-description.md` (strict sequence)

### Submission Workflow

1. Create a GitHub issue describing the change.
2. Generate an ADR from the template at:
   `docs/architecture/templates/adr-template.md`
3. Submit via Pull Request.
4. OPA policies validate:

   * Numbering
   * Structure
   * Required sections
   * Title format
   * Governance constraints
5. Human approval required before merge.

### Example ADRs

* `adr-000-hybrid-dag-mesh-architecture.md`
* `adr-001-orchestrator-governance-model.md`
* `adr-002-event-sourcing-strategy.md`

---

## Open Policy Agent (OPA)

OPA policies ensure governance integrity.

* **Policy Location:** `docs/governance/policies/adr_policy.rego`

### Enforced Constraints

* ADRs must originate from Pull Requests
* No numbering gaps
* Required sections must exist
* Mesh schemas must respect `allowed_edges`
* Mesh cannot modify Core DAG rules

### Run Policy Checks

```bash
./conftest test docs/architecture/design/ \
  --policy docs/governance/policies/adr_policy.rego \
  --namespace sdlc.governance
```

---

# Contributing

## Proposing Architectural Changes

Checklist:

* Proper sequential ADR number
* Kebab-case filename
* Problem / Solution / Rationale / Alternatives / Impact sections
* Template-based structure
* OPA policy checks pass
* Linked GitHub issue

## Submitting Code

Checklist:

* PR references ADR
* Unit and integration tests included
* Governance checks pass
* Code style validated via `golangci-lint`
* Documentation updated

---

# Repository Structure

```
sdlc-ide/
├── docs/
│   ├── architecture/
│   │   ├── design/
│   │   └── templates/
│   └── governance/
│       └── policies/
├── pkg/
│   ├── orchestrator/
│   ├── managers/
│   ├── mesh/
│   ├── events/
│   └── models/
├── agents/
├── orchestrator/
├── scripts/
├── helm/
├── cicd.yml
├── docker-compose.yml
└── README.md
```

---

# Practical Examples

## 1. PRD → TSD → ADR → KB Workflow

A complete end-to-end governed flow is provided in examples.

## 2. Mesh Extension Definition

Includes schema declaration and OPA validation steps.

## 3. Event Emission and Agent Reaction

Includes compliance violation scenario and agent response sequence.

---

# Deployment

## Local Development

```bash
docker-compose up -d
```

## Staging

```bash
helm install sdlc-ide sdlc-ide/sdlc-ide \
  --namespace staging \
  --values helm/values-staging.yaml
```

## Production

```bash
helm upgrade --install sdlc-ide sdlc-ide/sdlc-ide \
  --namespace production \
  --values helm/values-production.yaml \
  --wait --timeout 10m
```

---

# Troubleshooting

Common categories include:

* ADR Policy Validation Fails
* Orchestrator Not Detecting Documents
* Mesh Extension Rejected
* Event Stream Lagging

Each includes recommended commands, diagnostics, and root causes.

---

# Support & License

## Community

* Issues: https://git.chen.software/rad:zcmrr8AZD7dcRwAKnXBroJKyT2En/i
* Discussions: Discussions
* Slack: `#sdlc-ide`

## License

MIT License. See `LICENSE`.
