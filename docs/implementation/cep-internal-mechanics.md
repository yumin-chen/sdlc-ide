# CEP Internal Mechanics: A Deep Dive

This document provides a detailed technical breakdown of the internal mechanisms that modern Complex Event Processing (CEP) engines use to handle state, timing, and correctness. It is intended for engineers who are implementing, tuning, or debugging CEP patterns.

This guide complements the architectural overview in [ADR-001](../architecture/design/adr-001-complex-event-processing-engine.md) and the practical examples in the [CEP Implementation Guide](./cep-examples-and-comparison.md).

## 1. NFA Instance Branching (Greedy / Repeating Patterns)

**Context**: Greedy or repeating patterns (like `oneOrMore()`, `times()`, or `A+`) require the engine to track all possible partial matches simultaneously because each new event may extend existing partial matches or start a new one.

**How it works internally**:
*   **Partial Matches → NFA Instances**: Each time an event matches a step, the engine may spawn a new NFA instance for the same key to represent a possible match.
*   **Branching Example**: For a pattern `A B+ C` with incoming events `A1, B1, B2, C1`:
    1.  **Event A1 arrives** → A new NFA instance, `#1`, is created to represent the partial match `[A1]`.
    2.  **Event B1 arrives** → Instance `#1` progresses to `[A1, B1]`. To handle the `B+` (one or more B's), the engine also creates a new internal branch or a separate instance, `#2`, representing the same state. This allows the engine to explore multiple paths.
    3.  **Event B2 arrives** → Instance `#1` extends its match to `[A1, B1, B2]`, while instance `#2` might progress to `[A1, B2]`. Multiple branches now exist.
    4.  **Event C1 arrives** → Both active instances may consume `C1` and reach the `FINAL` state, emitting multiple valid matches (e.g., `[A1, B1, C1]` and `[A1, B1, B2, C1]`).
*   **Result**: Multiple NFA instances (or internal branches) represent all valid partial match sequences. This branching is what allows the engine to generate all possible overlapping matches.
*   **Memory Implication**: Without bounding (via time windows or max repetitions), this can explode the state size exponentially. This is the primary motivation for watermark-driven eviction.

## 2. Event-Time Timers and Temporal Constraints (`within(...)`)

*   **Purpose**: To ensure that matches respect temporal constraints (e.g., `A -> B within 5 seconds`).
*   **Implementation**:
    *   Each partial match (NFA instance) stores an event-time timer corresponding to its start event's timestamp plus the temporal constraint.
    *   When the system's watermark advances past this timer's timestamp, the engine evicts the NFA instance if it hasn’t yet reached a `FINAL` state.
*   **Example**:
    *   **Pattern**: `A -> B within 5 sec`
    *   **Event A arrives at t=10** → An event-time timer is scheduled for `t=15`.
    *   **Case 1: Event B arrives at t=14** → The instance completes, and the timer is cancelled.
    *   **Case 2: No B arrives** → When the watermark advances past `t=15`, any incomplete instances that started at `t=10` are automatically evicted.
*   **Benefit**: This guarantees memory-safe execution and provides deterministic, replayable handling of temporal rules.

## 3. Watermark-Driven Event Release and State Eviction

*   **Watermarks**: The watermark is the engine’s “commit point” in event time. It is an assertion that no more events with a timestamp less than or equal to the watermark will arrive.
*   **Temporal Buffer**: This buffer holds out-of-order events, sorting them by their event-time timestamps before they are processed.
*   **Event Release**: The engine only releases events from the buffer to the NFAs if their `EventTime ≤ Watermark`.
*   **State Eviction**: When the watermark passes the temporal deadline of an NFA instance (set by a `within` clause or an idle timeout), that instance is evicted automatically.

**Key Principle**: The NFA logic *never* sees out-of-order events. All disorder is handled transparently by the temporal buffer and the watermark mechanism, ensuring that the pattern semantics are clean and deterministic.

## 4. Late-Event Handling / Retractions

*   **Allowed Lateness (L)**: A configurable delay *after* the watermark has passed, during which the engine will still accept and process late events for a given window or pattern.
*   **Mechanism**:
    1.  If an event arrives with an `EventTime > (Watermark - L)`, the engine may re-open the state for the corresponding key and update the affected NFA instances.
    2.  This can trigger **retractions** (removing or correcting previously emitted matches) and re-computation.
    3.  Events with an `EventTime ≤ (Watermark - L)` are considered "too late" and are typically dropped or routed to a Dead Letter Queue (DLQ).
*   **Trade-off**:
    *   **Larger L**: Higher correctness, but at the cost of increased memory and compute (to maintain state longer and re-process events).
    *   **Smaller L**: Lower latency and memory usage, but a higher risk of dropping late events that could have corrected a result.

## 5. Consumption Policies (`SKIP_TO_NEXT`, `SKIP_PAST_LAST`)

These policies determine which partial matches are kept or discarded after a full match is found. They are critical for managing state and defining the desired matching behavior.

| Policy                | Behavior                                                                      | When to Use                                                        |
| --------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `SKIP_TO_NEXT`        | Discard the instance, and restart matching from the event that completed the match. | When no overlapping matches are needed. This significantly reduces memory usage. |
| `SKIP_PAST_LAST_EVENT`| Allows overlapping matches by keeping instances alive that could match future events. | Required for repeating patterns like `oneOrMore()` or `A+`.         |
| `NO_SKIP`             | Keep the instance in its final state. May produce duplicate results.           | Rarely used, as it can be highly memory-intensive and often leads to non-intuitive behavior. |

**Example with `A B+ C`**:
*   Using `SKIP_PAST_LAST_EVENT` (the typical default) keeps all partial match branches alive after each `B` event, allowing the engine to capture all possible sequences that eventually lead to a `C`.
*   Using `SKIP_TO_NEXT` would mean that once the first valid sequence completes (e.g., `[A, B1, C]`), all other partial matches that started from earlier `B` events are discarded, preventing overlapping results.
