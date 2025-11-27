
# Agent Interaction Model

## Overview
The SDLC_IDE leverages a highly decoupled, event-driven architecture for communication between its agents. This model ensures that agents are autonomous, resilient, and can be developed and scaled independently. The central nervous system of this architecture is an event stream, implemented using a durable and scalable messaging system like Apache Kafka.

## Event Backbone: Kafka
All inter-agent communication is mediated through a set of well-defined Kafka topics. This approach provides several key benefits:
- **Decoupling:** Agents do not need to have direct knowledge of each other. They simply produce and consume events from the relevant topics.
- **Asynchronicity:** Agents can process events at their own pace, without blocking other agents.
- **Auditability:** The event stream provides an immutable log of all significant events in the system, which is invaluable for auditing and debugging.

## Core Interaction Scenarios

### 1. New Artifact Creation
1. A user creates a new PRD.
2. The `Documentation Service` persists the PRD and emits an `Artifact_Created.v1` event to the `sdlc.docs.events` topic.
3. The `TraceabilityAgent` consumes this event and adds a new node to the document graph in the graph database.
4. The `Vectorization Service` also consumes the event, generates embeddings for the new PRD, and emits an `Artifact_Vectorized.v1` event.

### 2. Contradiction Detection
1. A user updates a TSD to link it to an existing PRD.
2. The `Documentation Service` emits an `Artifact_Updated.v1` event.
3. The `TraceabilityAgent` consumes this event and updates the document graph to reflect the new link.
4. The `ContradictionDetector` is also triggered by the `Artifact_Updated.v1` event. It uses the `TraceabilityAgent`'s graph to identify the linked PRD.
5. It then retrieves the embeddings for both the TSD and the PRD from the Vector DB and performs a semantic comparison.
6. If a contradiction is found, it emits an `Inconsistency_Detected.v1` event to the `sdlc.governance.events` topic.
7. The `Governor` agent consumes this event and decides on the appropriate action (e.g., notifying the user, blocking a merge).

### 3. Drift Detection
1. A developer pushes new code to the repository, which triggers a CI/CD pipeline.
2. The pipeline successfully builds and tests the code.
3. As a final step, the pipeline sends a webhook to the `DriftDetectorAgent`.
4. The `DriftDetectorAgent` fetches the latest code and performs static analysis.
5. It uses the `TraceabilityAgent` to find the TSD associated with the modified code.
6. It compares the analysis results with the TSD's content (potentially using embeddings for a more nuanced comparison).
7. If a significant divergence is found, it emits a `Drift_Detected.v1` event to the `sdlc.governance.events` topic.
8. The `Governor` agent consumes this event and takes appropriate action.

## Key Event Types
- `Artifact_Created.v1`: A new SDLC artifact has been created.
- `Artifact_Updated.v1`: An existing SDLC artifact has been updated.
- `Artifact_Deleted.v1`: An SDLC artifact has been deleted.
- `Artifact_Vectorized.v1`: The semantic embeddings for an artifact have been generated or updated.
- `Inconsistency_Detected.v1`: A semantic contradiction has been detected between two or more artifacts.
- `Drift_Detected.v1`: A divergence has been detected between the implementation and the technical specification.
- `Graph_Updated.v1`: The document relationship graph has been modified.
