---
title: "ADR-005: Orchestrator"
status: Pending
date: 2025-11-27
project: SDLC_IDE
author: System Architecture Team
---

## 1. Context

This ADR will define the architecture of the Orchestrator and Governor components of the SDLC_IDE. As outlined in ADR-001, these components are responsible for structural validation and policy enforcement.

### Required Updates from ADR-001

*   **Cycle detection + mesh validation algorithms:** This ADR must define the algorithms for validating mesh topology acyclicity and enforcing allowed edges to prevent DAG mutation.
*   **Core state machine:** This ADR will define the state machine for the core agents (PRD → TSD → ADR → KB).
*   **Transaction model:** In conjunction with ADR-004, this ADR will define the transaction model for atomic write operations.
*   **ACL model:** In conjunction with ADR-006, this ADR will define the ACL model for the system.
*   **Orchestrator MUST reject autonomous Core mutations:** This ADR must specify that the Orchestrator will reject any autonomous proposals attempting to mutate the Core DAG; such changes require a human-approved ADR.
