# ADR-003: Watermark Strategy for Event Time Processing

*   **Status:** Proposed
*   **Date:** 2024-05-14
*   **Deciders:** Jules (AI Agent)

## Context and Problem Statement

The Event-Based Observer Layer in the SDLC_IDE system processes a high volume of events in near real-time. To perform accurate time-based aggregations and windowing operations (e.g., "how many PRDs were updated in the last 5 minutes?"), we must use event time, not processing time. However, due to network latency and distributed producers, events can arrive out of order. Without a mechanism to track the progress of event time, the system cannot know when a time window is complete, leading to incorrect or delayed results.

## Decision Drivers

*   **Accuracy:** Time-based calculations must be accurate, even with out-of-order events.
*   **Latency:** The system should produce results with minimal delay.
*   **Resource Management:** The solution should avoid keeping excessive state in memory.
*   **Simplicity:** The chosen strategy should be easy to understand and implement.

## Considered Options

1.  **Strictly Ordered Ingestion:** Reject any event that arrives out of order. This is simple but impractical, as it would lead to significant data loss in a distributed system.
2.  **Punctuated Watermarks:** Each event source is responsible for emitting special "watermark" events that indicate the progress of event time. This is accurate but requires all sources to be well-behaved and coordinated.
3.  **Periodic Watermarks with a Bounded Out-of-Orderness:** The system periodically generates watermarks based on the maximum event timestamp seen so far, minus a fixed "lateness" bound. This is a robust and widely used strategy in stream processing.

## Decision Outcome

We will adopt **Periodic Watermarks with a Bounded Out-of-Orderness**. This strategy provides the best balance of accuracy, latency, and robustness.

The watermark will be calculated as `max(seen_event_time) - max_out_of_orderness_bound`. When the watermark advances past the end of a time window, the window is closed, and the results are emitted. Events that arrive after the watermark has passed their window are considered "late" and will be discarded or sent to a dead-letter queue.

### Positive Consequences

*   The system can handle a configurable amount of event lateness.
*   The watermark generation is centralized and does not rely on the behavior of individual event sources.
*   This approach is well-understood and has been battle-tested in systems like Apache Flink and Google Cloud Dataflow.

### Negative Consequences

*   Choosing the `max_out_of_orderness_bound` is a critical configuration parameter that requires tuning. If the bound is too small, data will be lost. If it's too large, results will be delayed.
*   Events that arrive later than the bound will be dropped, which may not be acceptable for all use cases.

## Links

*   [The Dataflow Model: A Practical Approach to Balancing Correctness, Latency, and Cost in Massive-Scale, Unbounded, Out-of-Order Data Processing](https://storage.googleapis.com/pub-tools-public-publication-data/pdf/43864.pdf)
*   [Apache Flink - Event Time and Watermarks](https://nightlies.apache.org/flink/flink-docs-release-1.14/docs/dev/datastream/event-time/)
