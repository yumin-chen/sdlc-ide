
---
Agent: ContradictionDetector
---

## Responsibility
Identifies conflicting requirements and statements across different SDLC artifacts, specifically:
- Product Requirements Documents (PRD)
- Technical Specification Documents (TSD)
- Architectural Decision Records (ADR)

The primary goal is to surface contradictions that are semantically incompatible, even if they don't share keywords. For example:
- PRD: "The system must support 100,000 concurrent users."
- TSD: "The system will be deployed as a single-instance Node.js application."

## Input
- **From:** Event Stream (Kafka Topic: `sdlc.docs.events`)
- **Via:** Subscribes to events of type `Artifact_Updated.v1` and `Artifact_Vectorized.v1`.

## Output
- **To:** `Governor` Agent and `Notification` Service.
- **Via:** Emits an `Inconsistency_Detected.v1` event to the `sdlc.governance.events` topic.

## Decision Points
- **Severity Threshold:** The agent will calculate a "contradiction score" based on the cosine distance of the embeddings. A configurable threshold (e.g., >0.8) will determine if the contradiction is severe enough to flag.
- **Auto-block vs. Advisory:** Initially, all contradictions will be advisory. The `Governor` agent will make the final decision on whether to block a change based on the severity and the context.

## Failure Modes
- **False Positives:** If the agent flags a non-contradiction, the event can be marked as a false positive by a human reviewer. This feedback will be used to fine-tune the embedding model.
- **Missed Contradictions:** If the agent fails to detect a contradiction, it represents a model failure. Regular model re-training and evaluation will be necessary to minimize this.

## State Machine
1. `LISTENING`: The agent is actively monitoring the event stream for relevant artifact updates.
2. `ANALYZING`: Upon receiving an `Artifact_Updated.v1` event, the agent retrieves the vectorized content of the updated artifact and its linked artifacts. It then computes the semantic similarity between the relevant statements.
3. `FLAGGING`: If a contradiction is detected, the agent transitions to this state, emits the `Inconsistency_Detected.v1` event, and waits for acknowledgment from the `Governor`.
4. `WAITING_FOR_REVIEW`: The agent remains in this state until a human provides feedback on the flagged inconsistency.

## Embedding/Semantic Role
- The agent heavily relies on a Vector DB for storing and querying text embeddings.
- It will cluster requirement statements by semantic meaning to identify outliers and potential contradictions.
- The choice of embedding model is crucial; it must be trained or fine-tuned on a corpus of technical and project management documents to understand the nuances of the domain.

## Dependencies
- **Vector DB:** For storing and querying embeddings.
- **TraceabilityAgent:** To understand the relationships and dependencies between different artifacts.
- **Governor Agent:** To enforce policies based on the detected contradictions.
