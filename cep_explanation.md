# CEP Internals Explained: NFA Lifecycle and Event Time Handling

This document details two core concepts in Complex Event Processing (CEP): the lifecycle of Non-deterministic Finite Automaton (NFA) instances and the mechanisms for handling out-of-order events.

---

### 1. NFA Instance Lifecycle: Creation, Progression, and Eviction

A CEP engine's primary job is to find sequences of events that match a user-defined pattern. It does this by compiling the pattern into a state machine (an NFA) and then creating instances of that NFA at runtime as events are processed.

#### a. NFA Instance Creation

- **Trigger**: An NFA instance is created when an incoming event matches the **first step** of a pattern.
- **Example Pattern**: `(Event A, key=X) -> (Event B, key=X) within 5 minutes`
- **Process**:
    1. An event `A1` with `key=X` arrives.
    2. The CEP engine sees that `A1` matches the starting state of the pattern.
    3. It creates a **new partial match** (an NFA instance). This instance is essentially a small, stateful object that stores a reference to event `A1` and knows that the *next* expected event is `B`.
    4. The instance is keyed by `X`, so it is processed in a partition dedicated to that key. This allows the engine to handle millions of parallel patterns for different keys (`X`, `Y`, `Z`, etc.) without interference.

#### b. NFA Instance Progression

- **Trigger**: An existing NFA instance progresses when a subsequent event matches the *next* step in its pattern.
- **Process**:
    1. The partial match for `A1` (keyed by `X`) is now active and waiting.
    2. An event `B1` with `key=X` arrives.
    3. The engine checks its active NFA instances for the key `X`. It finds the one waiting for an event `B`.
    4. `B1` matches the predicate. The NFA instance transitions to its next state.
    5. In this simple two-step pattern, the instance has now reached its **final state**. The pattern has successfully matched. The engine emits a complex event (the result), containing information from both `A1` and `B1`.

#### c. NFA Instance Eviction (Termination)

An NFA instance cannot live forever; it must be garbage-collected to prevent memory leaks. This happens in two primary scenarios:

1.  **Successful Match**: After a pattern completes (like in the step above), its future behavior is determined by the **`AfterMatchSkipStrategy`**.
    -   `SKIP_TO_NEXT`: The instance is discarded. A new instance can be started by the *next* event A. This is the most common and memory-safe option.
    -   `NO_SKIP`: The instance is *not* discarded and tries to find another match starting from its current state. This is for advanced use cases and can lead to overlapping matches and higher memory use.

2.  **Timeout / Expiration**: The NFA instance is evicted if it fails to complete within a specified time window.
    -   **Trigger**: The pattern `... within 5 minutes` compiles into a timer on the NFA state.
    -   **Process**: When the NFA instance for `A1` was created, the engine also scheduled a **timer event** to fire in 5 minutes *event time*.
    -   If a matching `B` event does not arrive before the system's **Watermark** advances past that 5-minute mark, the timer event is triggered.
    -   The engine then **discards (evicts)** the partial match for `A1` to free up resources. This is critical for preventing "state explosion," where the system is clogged with partial matches that will never complete.

---

### 2. Handling of Late and Out-of-Order Events

Real-world systems have network lag and distributed sources, so events often do not arrive in the order they were generated. CEP engines must handle this to ensure correctness.

#### a. The Problem: Processing Time vs. Event Time

-   **Processing Time**: The wall-clock time when the CEP engine *sees* the event. Unreliable for ordering.
-   **Event Time (`t_event`)**: The timestamp embedded in the event, indicating when it *actually occurred* at the source. This is the source of truth.

If we process events in the order they arrive (Processing Time), a sequence `A (t=10:00:01) -> B (t=10:00:02)` might be missed if event `B` arrives at the engine *before* `A` due to a network delay.

#### b. The Solution: Watermarks and a Temporal Buffer

The engine uses two key mechanisms to solve this:

1.  **Temporal Buffer**:
    -   When events arrive, they are not processed immediately. Instead, they are placed into an internal buffer, sorted by their **Event Time**.
    -   Example: `B (t_event=10:00:02)` arrives first, followed by `A (t_event=10:00:01)`. The buffer re-orders them correctly: `[A(t=10:00:01), B(t=10:00:02)]`.

2.  **Watermarks (W)**:
    -   A Watermark is a special timestamp that flows through the event stream. It is a declaration from the CEP engine: **"I am now confident that no more events with an Event Time earlier than `W` will ever arrive."**
    -   The engine generates watermarks based on the event times it has observed, typically using a strategy like `WatermarkStrategy.forBoundedOutOfOrderness(L)`, where `L` is the maximum expected lateness.
    -   The Watermark `W` acts as a **trigger**. When `W = 10:00:05`, the engine knows it is safe to take all events from the temporal buffer with `t_event <= 10:00:05` and feed them to the NFA instances **in strict Event Time order**.

#### c. Handling "Late" Events

-   An event is considered "late" if its Event Time is less than the current Watermark.
-   Example: The current Watermark is `W = 10:00:15`. An event `C (t_event=10:00:10)` arrives.
-   This event is **late**. The system has already declared it will not see events older than `10:00:15`.
-   The engine will typically **drop** this late event or route it to a Dead Letter Queue (DLQ) for separate analysis. This is a trade-off between correctness and resource management; waiting indefinitely for late events would require infinite memory. The `LatenessThreshold` (`L`) is a configurable buffer to accommodate expected delays without dropping too many events.
