---
title: "ADR-006: Custom Integration"
status: Pending
date: 2025-11-27
project: SDLC_IDE
author: System Architecture Team
---

## 1. Context

This ADR will define the process and requirements for integrating custom document types and agents into the SDLC_IDE's Mesh Layer. As outlined in ADR-001, all extensions must be explicitly declared and validated.

### Required Updates from ADR-001

*   **Extension schema + edge declarations:** This ADR must define the schema for declaring custom document types, including their allowed inbound/outbound edges, embedding strategy, and lifecycle state.
*   **ACL model:** In conjunction with ADR-005, this ADR will define the ACL model for custom integrations.
*   **Validation process:** This ADR will detail the process by which custom integrations are validated by the Orchestrator and Governor.
