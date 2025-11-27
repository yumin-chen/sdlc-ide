---
title: "ADR-004: Persistence"
status: Pending
date: 2025-11-27
project: SDLC_IDE
author: System Architecture Team
---

## 1. Context

This ADR will define the architecture for the persistence layer and workspace of the SDLC_IDE. As outlined in ADR-001, the workspace must be version-controlled and enforce DAG semantics.

### Required Updates from ADR-001

*   **Workspace enforces DAG + mesh topology:** The workspace structure must reflect the core and mesh topology, and all writes must be enforced by the Orchestrator. The directory structure will be `.sdlc_ide/core/` for core artifacts and `.sdlc_ide/extensions/` for mesh extensions.
*   **Transaction Model:** This ADR, in conjunction with ADR-005, will define the transaction model for atomic write operations.
