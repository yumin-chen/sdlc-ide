---
title: "ADR-003: Vectorization"
status: Pending
date: 2025-11-27
project: SDLC_IDE
author: System Architecture Team
---

## 1. Context

This ADR will define the architecture for vectorization and embedding of documents within the SDLC_IDE. As outlined in ADR-001, embeddings are used for semantic linking and do not override structural rules.

### Required Updates from ADR-001

*   **Embeddings must defer to Orchestrator:** The embedding strategy must defer to the orchestrator and schema validation for all structural rules. Semantic inference is a separate, non-authoritative process.
