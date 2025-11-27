---
title: "ADR-002: Event Streaming"
status: Pending
date: 2025-11-27
project: SDLC_IDE
author: System Architecture Team
---

## 1. Context

This ADR will define the architecture of the event streaming layer, which is a core component of the SDLC_IDE's observability and communication strategy. As outlined in ADR-001, this layer must be immutable, append-only, and schematized.

### Required Updates from ADR-001

*   **Ordering guarantees for DAG artifacts:** The event stream must provide causal ordering for events related to the Core DAG, likely by partitioning by `artifact_id` and using `Dependency_Evaluated` events.
*   **Observability of Mesh Extensions:** All extension proposals, approvals, and rejections **MUST** be emitted as immutable events to ensure full auditability of the system's autonomous evolution.
