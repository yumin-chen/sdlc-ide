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

Successful implementation requires addressing the performance-critical aspects of state management and pattern execution within the Flink CEP engine. This section outlines key tuning strategies and robust design principles.

### 7.1. Performance Tuning and State Management

High-performance CEP is critically dependent on minimizing the state space and maximizing parallelism.

*   **Partitioning (`KeyBy`)**: The `correlateBy` field in our pattern definition is the most critical tuning parameter. It translates directly to a `keyBy` operation in Flink. This partitions the NFA state, creating an independent state machine per key, which enables horizontal scaling and prevents state explosion. **Unkeyed, global patterns must be avoided for high-volume event streams.**

*   **State Backend**: For patterns that may run for hours or days, Flink's `RocksDB` state backend should be used to store state on disk, preventing memory exhaustion. Incremental checkpoints must be enabled to ensure fast and efficient fault tolerance.

*   **Watermark Strategy**: A correct watermark strategy is essential for handling out-of-order events. A `BoundedOutOfOrdernessTimestampExtractor` should be configured with a delay that reflects the observed event time skew in the system. A conservative delay increases latency and memory usage, while an aggressive delay risks dropping late events.

*   **Early Filtering**: The `where` clause in a pattern step allows for predicate push-down. This filtering occurs *before* an event is fed to the NFA, reducing the number of partial matches created and thus conserving resources.

### 7.2. Robust Pattern Design Principles

Pattern logic must be designed defensively to avoid performance traps and ensure predictable behavior.

#### 7.2.1. Safety Checklist

1.  **Bound Everything**: All patterns must have a clearly defined and conservative `within` clause. This guarantees that all partial matches are eventually garbage collected. Greedy quantifiers (e.g., repeating steps) must also be bounded.
2.  **Scope with Keys**: Every pattern must be scoped to a specific context using `correlateBy`. This is the primary mechanism for controlling state size.
3.  **Make Negation Specific**: Negation (`notFollowedBy`) is the most expensive operation. It should always be used with a short time window and be tightly coupled to the correlation key.
4.  **Choose a Conscious Consumption Policy**: The `CEP_Agent` will default to a `SKIP_PAST_LAST_EVENT` strategy (`AfterMatchSkipStrategy` in Flink). This provides the most intuitive behavior by preventing a single event from being part of multiple successful matches of the same pattern.
5.  **Handle Timeouts as Events**: A pattern that does not complete is often as significant as one that does. The `CEP_Agent` should be configured to emit timeout events, allowing downstream systems to observe and react to the absence of expected event sequences.

#### 7.2.2. Common Anti-Patterns to Avoid

*   **Greedy Quantifiers**: Avoid repeating steps (`oneOrMore()`, `timesOrMore()`) without a strict `within` clause. This can lead to an exponential state explosion.
*   **Unconstrained Correlation**: A pattern without a `correlateBy` key will operate on a global, unpartitioned stream, which is not scalable.
*   **The "Heavy Negation" Trap**: Using `notFollowedBy` with a long time window can force the engine to keep state for an extended period, leading to high memory pressure. Keep negation windows as short as possible.
