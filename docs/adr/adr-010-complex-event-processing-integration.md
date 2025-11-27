---
title: 'ADR-010: Complex Event Processing (CEP) Integration'
status: 'Proposed'
date: '2025-11-27'
---

## 1. Title

ADR-010: Complex Event Processing (CEP) Integration for Advanced SDLC Observability

## 2. Status

Proposed

## 3. Context

The SDLC_IDE generates a high-volume stream of events representing fine-grained actions within the software development lifecycle (e.g., `PRD_Updated`, `TSD_Updated`, `ContradictionDetected`). While individual events are useful, they do not capture the temporal relationships, sequences, or absences of events that often signify important business processes, compliance violations, or quality deviations.

To unlock this next level of observability, we need a mechanism to detect and react to complex patterns of events over time. This requires a specialized engine capable of handling event-time semantics, stateful pattern matching, and temporal windows.

Key requirements include:
-   **Detecting process non-compliance:** E.g., a `TSD_Updated` event is not followed by an `ADR_Updated` event within a defined SLA.
-   **Identifying quality anti-patterns:** E.g., a high frequency of `ContradictionDetected` events related to the same artifact.
-   **Automating governance:** E.g., flagging a `Deployment_Approved` event that was not preceded by a `SecurityScan_Passed` event.
-   **Supporting declarative patterns:** Business rules and patterns should be defined in a human-readable, version-controlled format, separate from the engine's implementation.

## 4. Decision

We will integrate a Complex Event Processing (CEP) engine into the SDLC_IDE architecture to enable the detection of meaningful event patterns.

### 4.1. Technology Choice: Apache Flink

We will use **Apache Flink** as the underlying CEP engine. Flink is a state-of-the-art, open-source stream processing framework with a powerful and mature CEP library.

**Justification:**
1.  **First-Class Event-Time Semantics:** Flink is designed to handle out-of-order events and correctly reason about time-based patterns using event-time, which is critical for accurately modeling real-world processes.
2.  **Stateful Processing:** It provides robust, scalable, and fault-tolerant state management, which is essential for tracking long-running patterns that may last hours or days.
3.  **Scalability:** Flink can scale from a single node to large clusters, ensuring the system can handle future growth in event volume.
4.  **Expressive CEP API:** Flink's CEP library provides a rich set of pattern-matching semantics, including sequencing, negation, time windows, and flexible correlation logic.
5.  **Ecosystem Integration:** It integrates seamlessly with event streaming platforms like Kafka, Pulsar, or NATS, which are already specified in ADR-002.

### 4.2. Architectural Placement

The CEP capability will be implemented as a new type of agent, the `CEP_Agent`, which operates within the **Event-Based Observer Layer**.

-   The `CEP_Agent` subscribes to the raw event stream from the event backbone.
-   It loads a set of declarative pattern definitions (see Section 4.3) from the `.sdlc_ide/patterns/` directory.
-   For each incoming event, it evaluates the event against all active patterns using the Flink CEP engine.
-   When a pattern is successfully matched, the `CEP_Agent` emits a new, higher-order event, `Complex_Event_Detected`, onto the event stream. This new event contains details of the pattern that was matched and the constituent events.

This placement ensures that CEP is a non-intrusive, purely observational component. It does not modify the Core DAG or Mesh Layer, adhering to the architectural principle of separating observation from orchestration (ADR-001).

### 4.3. Declarative Pattern Definitions

CEP patterns will be defined declaratively in YAML files stored in the repository at `.sdlc_ide/patterns/`. This approach decouples the pattern logic from the agent's implementation, allowing architects, project managers, and other stakeholders to define and manage rules without writing code.

A JSON schema will be created to formalize the structure of these YAML definitions (see ADR-010 artifacts).

## 5. Consequences

### Positive
-   **Enhanced Observability:** Enables deep, process-aware monitoring of the entire SDLC.
-   **Automated Governance:** Proactively detects and flags compliance deviations and anti-patterns, reducing manual oversight.
-   **Flexibility:** The declarative pattern model allows for the rapid development and deployment of new business rules and insights.
-   **Decoupled Architecture:** The `CEP_Agent` is an independent observer and does not increase the complexity of the core orchestration logic.

### Negative
-   **Increased Operational Complexity:** Introduces Apache Flink as a new component in the technology stack, which requires operational expertise to deploy, manage, and monitor.
-   **State Management Overhead:** The Flink engine will maintain state for all active patterns, which requires careful resource management (memory, disk).
-   **Potential for "Rule Sprawl":** The ease of creating new patterns could lead to a large, unmanageable set of rules if not properly curated and governed. A clear ownership and review process for patterns will be necessary.

## 6. Open Questions

1.  What is the formal process for reviewing, approving, and deploying new CEP pattern definitions?
2.  How will the performance and resource consumption of the `CEP_Agent` be monitored?
3.  What is the strategy for testing CEP patterns before they are deployed to production?

## 7. Advanced Implementation Considerations

While the high-level architecture is defined, successful implementation requires addressing the performance-critical aspects of state management and pattern execution within the Flink CEP engine.

### 7.1. State Management Performance Tuning

High-performance CEP is critically dependent on efficient state management to prevent memory exhaustion and ensure low-latency processing. The following techniques must be employed:

*   **State Explosion Prevention**:
    *   **Early Filtering**: Conditions in patterns (the `where` clause) should be evaluated before an event is fed to the NFA engine. This reduces the number of NFA instances spawned.
    *   **Partitioning by Correlation Keys**: Using the `correlateBy` field is essential. Flink will create separate, independent state machines for each key, enabling data locality and massive parallelization.
    *   **Aggressive State Eviction**: Temporal windows (`within` clauses) must be as short as functionally possible. Long-running patterns will inherently consume more memory and must be provisioned accordingly.

*   **Efficient Window Structures**: Flink's internal data structures (like append-only logs with watermark sweeping) are highly optimized. The key is to provide a correct and efficient watermarking strategy to allow the engine to prune old state effectively.

*   **Shared Automata Prefixes**: When multiple patterns share a common starting sequence (e.g., `A -> B -> C` and `A -> B -> D`), the Flink engine is capable of sharing the state for the common prefix (`A -> B`), significantly reducing memory overhead.

### 7.2. Optimization of Negation Detection (`notFollowedBy`)

Negation is one of the most powerful but computationally expensive features in CEP. A `notFollowedBy` clause requires the engine to maintain state for a period of time, waiting for an event that *doesn't* happen.

*   **The Challenge**: For every partial match that enters a state with a negation condition, the engine must monitor subsequent events for the negated event type. This can create significant overhead.
*   **Optimization Strategy**: The most effective optimization is to **always combine negation with strong correlation keys**. For example, in the `tsd-adr-sla.v1.yaml` pattern, the negation (`notFollowedBy: ADR_Updated`) is tied to the `artifact.id` of the preceding `TSD_Updated` event. This scopes the negation watcher to only look for an `ADR_Updated` event with the *same artifact ID*, drastically reducing the search space. Uncorrelated, global negation patterns should be avoided as they are not scalable.

### 7.3. Consumption Policies (Skip Strategies)

When a pattern can match multiple times starting from the same event, a consumption policy (or "skip strategy") defines what happens after a match is found.

*   **`NO_SKIP` (Default)**: After a match, the engine will look for all other possible matches starting from the same event. (e.g., `A B1 B2` could match `A -> B` twice).
*   **`SKIP_PAST_LAST_EVENT`**: After a match is found (e.g., `A -> B`), the engine resumes the search *after* the event that completed the match (`B`). This is the most common and intuitive strategy.
*   **`SKIP_TO_NEXT`**: If multiple patterns could start at the same event, this strategy discards any partial matches that began at the same location once one of them completes.

The declarative pattern schema will default to the `SKIP_PAST_LAST_EVENT` behavior, as it is the most predictable for process compliance use cases. This can be made configurable in future versions of the schema if required.
