# SDLC_IDE: Multi-Agent System for Software Development Lifecycle Management

A governance-first, extensible multi-agent framework for managing software development artifacts and workflows. SDLC_IDE combines deterministic core processes with flexible, user-defined extensions to balance compliance rigor and operational agility.

## Quick Start

### Prerequisites

- Go 1.21+
- Docker & Docker Compose
- Open Policy Agent (OPA)
- Conftest
- Helm 3.0+

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/sdlc-ide.git
cd sdlc-ide

# Install OPA and Conftest
curl https://openpolicyagent.org/downloads/latest/opa_linux_x86_64 -o opa
chmod +x ./opa

curl -L https://github.com/open-policy-agent/conftest/releases/download/v0.46.0/conftest_0.46.0_Linux_x86_64.tar.gz -o conftest.tar.gz
tar xf conftest.tar.gz

# Verify governance policies locally
./conftest test docs/architecture/design/ \
  --policy docs/governance/policies/adr_policy.rego \
  --namespace sdlc.governance

# Run tests
go test -v ./...

# Build and run locally
docker-compose up -d
```

## Architecture Overview

SDLC_IDE is built on three integrated layers:

### 1. Core Directed Acyclic Graph (DAG)

The immutable backbone of the SDLC workflow:

```
PRD → TSD → ADR → KB
```

**Document Types:**
- **PRD** — Product Requirements Document
- **TSD** — Technical Specification Document
- **ADR** — Architecture Decision Record
- **KB** — Knowledge Base Archive

**Properties:**
- Deterministic, rule-enforced transitions
- Orchestrator-governed state changes
- Fully auditable lifecycle events
- No autonomous agent modifications without formal approval

### 2. Selective Mesh Extension Layer

Flexible, user-defined document types and relationships that extend (but never override) the Core DAG.

**Supported Extensions:**
- API Specifications
- Compliance Documents
- Performance Models
- Custom Project Artifacts

**Constraints:**
- Declarative schemas with allowed edges
- Local communication within Mesh clusters
- Semantic (embedding-based) links enabled
- All changes validated by Orchestrator + Governor

### 3. Event-Based Observer Layer

Immutable event stream capturing all lifecycle and communication activity.

**Capabilities:**
- Emit structured lifecycle events
- Enable ML-driven insights and recommendations
- Provide analytics for compliance and performance
- Do not directly influence Core DAG structure

## Key Principles

### Human-Governed Core
The Core DAG remains immutable to autonomous agents. All modifications require formal Architecture Decision Record (ADR) approval through the PR workflow.

### Agent-Driven Extensibility
Agents propose new Mesh document types and relationships. All proposals are validated against governance policies and approved by the Orchestrator before deployment.

### Single Source of Authority (SSoA)
The Core DAG is the canonical SDLC definition. Mesh extensions enrich semantic understanding but never override lifecycle rules.

### Strong Separation of Concerns
Core and Mesh evolve independently with strict boundary enforcement, minimizing systemic risk and enabling safe experimentation.

## Governance & Compliance

### Architecture Decision Records (ADRs)

All architectural decisions are formally documented and version-controlled.

**Location:** `docs/architecture/design/`

**Naming Convention:**
```
adr-XXX-kebab-case-description.md
```

Where `XXX` is a strictly sequential number (000, 001, 002, etc.).

**Submission Process:**
1. Create ADR file using template: `docs/architecture/templates/adr-template.md`
2. Include rationale, alternatives, and expected impact
3. Submit via Pull Request (direct commits disallowed)
4. Governance policies automatically validate numbering and formatting
5. Merge only after approval

**Example ADRs:**
- `adr-000-hybrid-dag-mesh-architecture.md` — Core architecture
- `adr-001-orchestrator-governance-model.md` — Agent authorization
- `adr-002-event-sourcing-strategy.md` — Audit logging

### Open Policy Agent (OPA)

Governance policies are enforced programmatically using OPA.

**Policy Location:** `docs/governance/policies/adr_policy.rego`

**Enforced Constraints:**
- ADR changes must originate from Pull Requests
- ADR numbering must be sequential without gaps
- Title formatting must follow project conventions
- Mesh extensions cannot override Core DAG transitions
- All document schemas validated against allowed_edges

**Run Policy Checks:**
```bash
conftest test docs/architecture/design/ \
  --policy docs/governance/policies/adr_policy.rego \
  --namespace sdlc.governance
```

## Contributing

### Proposing Architectural Changes

1. **Open an issue** describing the change and its rationale
2. **Create an ADR** using the template
3. **Submit a PR** linking the issue and ADR
4. **Wait for governance validation** (OPA checks run automatically)
5. **Address feedback** from reviewers
6. **Merge** once approved

**Checklist:**
- [ ] ADR follows naming convention: `adr-XXX-kebab-case-description.md`
- [ ] ADR uses approved template from `docs/architecture/templates/adr-template.md`
- [ ] Rationale section explains the "why"
- [ ] Alternatives section covers rejected approaches
- [ ] Impact section identifies affected systems
- [ ] OPA policy checks pass locally
- [ ] PR description links to related issue

### Submitting Code Changes

All code changes should reference related ADRs.

**PR Template:**
```
## Description
Brief summary of changes

## Related ADR
Refs #adr-XXX

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Governance checks pass

## Checklist
- [ ] Code follows project style guide
- [ ] Self-review completed
- [ ] Tests provide adequate coverage
```

### Running Tests Locally

```bash
# Unit tests
go test -v -coverprofile=coverage.out ./...
go tool cover -func coverage.out

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Governance compliance
conftest test docs/architecture/design/ \
  --policy docs/governance/policies/adr_policy.rego \
  --namespace sdlc.governance

# Code quality
golangci-lint run ./...
```

## Repository Structure

```
sdlc-ide/
├── docs/
│   ├── architecture/
│   │   ├── design/
│   │   │   ├── adr-000-hybrid-dag-mesh-architecture.md
│   │   │   ├── adr-001-orchestrator-governance-model.md
│   │   │   └── ... (sequential ADRs)
│   │   └── templates/
│   │       └── adr-template.md
│   └── governance/
│       └── policies/
│           └── adr_policy.rego
├── pkg/
│   ├── orchestrator/      # Core orchestration logic
│   ├── managers/          # DAG document managers
│   ├── mesh/              # Extension layer implementations
│   ├── events/            # Event stream & observers
│   └── models/            # Data structures
├── agents/
│   ├── proposal_agent/    # ADR & Mesh proposal generation
│   ├── compliance_agent/  # Policy validation
│   └── insight_agent/     # Analytics & recommendations
├── orchestrator/
│   ├── main.go
│   ├── config.yaml
│   └── handlers/
├── scripts/
│   └── validate_schemas.py
├── helm/
│   ├── values.yaml
│   ├── values-staging.yaml
│   └── values-production.yaml
├── docker-compose.yml
├── docker-compose.test.yml
├── Dockerfile
├── cicd.yml               # CI/CD pipeline configuration
└── README.md
```

## Practical Examples

### Example 1: Creating a PRD → TSD Workflow

```bash
# 1. Create PRD document
cat > docs/sdlc/prd-001.md << EOF
# PRD: User Authentication

## Overview
Implement OAuth2-based authentication...

## Requirements
- Support multiple identity providers
- Maintain session state
- Enable SSO capabilities
EOF

# 2. Orchestrator detects new PRD and registers it
# (Automatic via event watcher)

# 3. Create corresponding TSD
cat > docs/sdlc/tsd-001.md << EOF
# TSD: Auth Service Implementation

## Overview
Technical implementation of PRD-001...

## Architecture
- OAuth2 provider integration
- Session management strategy
- API specifications in /specs/auth-api.yaml

## References
- PRD: prd-001.md
EOF

# 4. Orchestrator automatically links TSD to PRD in Core DAG
# State transitions: PRD (active) → TSD (in_progress)
```

### Example 2: Defining a Mesh Extension

```yaml
# mesh/extensions/compliance-report.yaml
name: Compliance Report
version: "1.0"

schema:
  properties:
    author:
      type: string
      description: "Report author"
    date:
      type: string
      format: "YYYY-MM-DD"
    report_content:
      type: string
    compliance_level:
      type: string
      enum: [full, partial, non_compliant]

allowed_edges:
  - type: references
    target: TSD
    description: "Links to technical specifications"
  - type: references
    target: ADR
    description: "References architectural decisions"

validation_rules:
  - author_required: true
  - date_in_past: true
  - report_length_min: 100
```

### Example 3: Event Emission & Subscription

```json
{
  "event_id": "evt-20240115-001",
  "timestamp": "2024-01-15T10:30:00Z",
  "event_type": "compliance_violation",
  "source": "compliance_agent",
  "document_id": "tsd-001",
  "document_type": "TSD",
  "message": "TSD-001 does not comply with security policy ADR-003",
  "severity": "high",
  "recommended_action": "Update TSD-001 to align with ADR-003 before progression to ADR stage",
  "related_adr": "adr-003-security-requirements",
  "tags": ["security", "compliance", "requires_review"]
}
```

## Deployment

### Local Development

```bash
docker-compose up -d
# Services: orchestrator, event-store, policy-engine
```

### Staging Environment

```bash
helm repo add sdlc-ide https://charts.example.com/sdlc-ide
helm install sdlc-ide sdlc-ide/sdlc-ide \
  --namespace staging \
  --values helm/values-staging.yaml
```

### Production Deployment

```bash
helm upgrade --install sdlc-ide sdlc-ide/sdlc-ide \
  --namespace production \
  --values helm/values-production.yaml \
  --wait
```

## API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/documents` | GET | List all documents in Core DAG |
| `/api/v1/documents/{id}` | GET | Retrieve document details |
| `/api/v1/documents` | POST | Create new document (PRD) |
| `/api/v1/transitions/{id}` | POST | Request state transition (ADR-gated) |
| `/api/v1/mesh/extensions` | GET | List all Mesh extensions |
| `/api/v1/events` | GET | Stream lifecycle events |
| `/api/v1/governance/validate` | POST | Validate document against policies |

## Monitoring & Observability

### Key Metrics

- `sdlc_document_lifecycle_duration` — Time from PRD to KB
- `sdlc_orchestrator_latency` — Orchestrator decision latency
- `sdlc_policy_violations` — Count of governance violations
- `sdlc_agent_proposals_pending` — Queued Mesh proposals

### Logging

All lifecycle events are logged to centralized event store with full audit trails.

```bash
# Query recent compliance violations
curl http://localhost:8080/api/v1/events?type=compliance_violation&limit=100
```

## Troubleshooting

### ADR Policy Validation Fails

```bash
# Check policy syntax
conftest test docs/architecture/design/ \
  --policy docs/governance/policies/adr_policy.rego \
  --namespace sdlc.governance \
  --verbose
```

### Orchestrator Not Recognizing New Documents

1. Verify document schema matches `allowed_edges`
2. Check Orchestrator logs: `docker logs sdlc-orchestrator`
3. Ensure document is in correct directory: `docs/sdlc/`

### Mesh Extension Rejected by Governor

Review the governance policy output:
```bash
conftest test mesh/extensions/ \
  --policy docs/governance/policies/mesh_policy.rego
```

## Support & Community

- **Issues**: [GitHub Issues](https://github.com/your-org/sdlc-ide/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/sdlc-ide/discussions)
- **Documentation**: See `/docs` directory
- **Slack**: `#sdlc-ide` channel

## License

This project is licensed under the MIT License. See `LICENSE` file for details.

## Contributing Guidelines

See `CONTRIBUTING.md` for detailed contribution guidelines, code style, and development workflow.
