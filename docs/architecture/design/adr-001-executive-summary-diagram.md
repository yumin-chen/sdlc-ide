# ADR-001: Executive Summary Diagram

This diagram provides a high-level, "one-page" executive view of the Hybrid Directed Graph Architecture, suitable for stakeholder presentations. It illustrates the relationship between the three primary layers of the system at a glance.

```mermaid
graph TD
    subgraph "SDLC_IDE Architecture"
        direction LR

        subgraph "Authoritative Core (DAG)"
            direction TB
            A[PRD] --> B[TSD] --> C[ADR] --> D[Knowledge Base]
        end

        subgraph "Flexible Extensions (Mesh)"
            direction TB
            E[API Specs]
            F[Compliance Rules]
            G[Performance Models]
        end

        subgraph "System-Wide Layers"
            direction TB
            H{Orchestrator} -- Governs & Validates --> A
            H -- Governs & Validates --> B
            H -- Governs & Validates --> C
            H -- Governs & Validates --> D
            H -- Governs & Validates --> E
            H -- Governs & Validates --> F
            H -- Governs & Validates --> G
            I([Event Stream])
        end
    end

    %% Styling
    style A fill:#cde4ff,stroke:#6699ff
    style B fill:#cde4ff,stroke:#6699ff
    style C fill:#cde4ff,stroke:#6699ff
    style D fill:#cde4ff,stroke:#6699ff
    style E fill:#d5f5e3,stroke:#58d68d
    style F fill:#d5f5e3,stroke:#58d68d
    style G fill:#d5f5e3,stroke:#58d68d
    style H fill:#fff0b3,stroke:#ffc300,stroke-width:2px,stroke-dasharray: 5 5
    style I fill:#f2f2f2,stroke:#b3b3b3
```
