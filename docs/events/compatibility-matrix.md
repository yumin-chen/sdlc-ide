# Compatibility Matrix

| Event Type            | Latest Version | Compatibility Mode | Schema Evolution Status | Owned By | Last Updated | Notes               |
|-----------------------|----------------|--------------------|-------------------------|----------|--------------|---------------------|
| PRD_Updated           | v1             | BACKWARD           | Stable                  | PRM      | 2025-11-27   | Stable              |
| TSD_Updated           | v1             | BACKWARD           | Evolving                | TSM      | 2025-11-27   | Evolving schema     |
| Agent_Call            | v1             | BACKWARD           | Stable                  | PRM      | 2025-11-27   | Internal            |
| User_Interaction      | v1             | BACKWARD           | Stable                  | UI Team  | 2025-11-27   | High-volume         |
| Git_Commit            | v1             | BACKWARD           | Stable                  | DevOps   | 2025-11-27   | Mirrors git events  |
| Artifact_Vectorized   | v1             | BACKWARD           | Evolving                | AI Team  | 2025-11-27   | Embeddings evolve   |
| Policy_Violation      | v1             | BACKWARD           | Stable                  | Security | 2025-11-27   | Security-critical   |
