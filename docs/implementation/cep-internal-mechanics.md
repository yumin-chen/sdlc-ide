# CEP Internal Mechanics: A Deep Dive

This document provides a detailed technical breakdown of the core concepts that power the Complex Event Processing (CEP) engine. It is intended for engineers who are implementing, extending, or debugging the engine's internals.

## 1. NFA Instance Lifecycle: Creation, Progression, and Eviction

The NFA (Nondeterministic Finite Automaton) is the compiled, executable form of a declarative CEP pattern. An NFA Instance represents a specific, ongoing, partial match of that pattern sequence, usually tied to a specific key (e.g., a user session).

### A. Instance Creation (Start)

*   **Incoming Event**: An event, say Event E_1, arrives and is processed.
*   **Start State Transition**: If E_1 satisfies the predicate for the very first step of the pattern (the Start State), a new NFA Instance is created for that specific E_1.
*   **State Storage**: This new instance stores a reference to E_1 and moves its internal pointer to the next state (e.g., In-A).

### B. Instance Progression (Match & Advance)

*   **Subsequent Events**: A subsequent event, E_2, arrives and is fed to the NFA (in **Event Time** order, thanks to the temporal buffer).
*   **Transition Check**: The active NFA Instance checks if E_2 satisfies a transition predicate from its current state (e.g., the transition from In-A to In-B).
*   **Advancement**: If satisfied, E_2 is appended to the partial match sequence, and the instance moves to the next state (e.g., In-B).
*   **Completion**: If the instance reaches the Final State, a full pattern match is emitted. The engine then uses the configured Consumption Policy (e.g., SKIP_TO_NEXT) to decide whether to delete this instance or let it continue looking for overlapping matches.

### C. Instance Eviction (Timeout)

*   **Timer Setting**: If the pattern includes a temporal constraint, such as `A -> B within 5 minutes`, an Event-Time Timer is scheduled when the instance transitions to state In-B. This timer is set for **EventTime(E_A) + 5 minutes**.
*   **Watermark Firing**: The timer does not fire by wall clock. It fires only when the Watermark (W) advances past the timer's set time.
*   **Timeout**: When the timer fires, the CEP engine concludes that the required event (e.g., B) will not arrive in time. The partial match is considered expired (a TIMEOUT or ABSENCE event may be emitted), and the NFA Instance is evicted (deleted) to free up memory. This is critical for preventing memory leaks (state explosion).

## 2. Handling Late and Out-of-Order Events

The entire out-of-order mechanism hinges on separating **Event Time** from **Processing Time** using Watermarks and the Temporal Buffer.

### Out-of-Order Correction

*   **Mechanism**: The Temporal Buffer holds all incoming events and ensures that the NFA only sees events in strict **Event Time** order.
*   **Example**: If E_B (Event Time t=10:01) arrives physically before E_A (Event Time t=10:00):
    *   Both events enter the buffer.
    *   When the Watermark advances past t=10:01, the buffer releases E_A first, then E_B, maintaining the correct sequence order for the NFA.

### Lateness Management (The Trade-Off)

The **Watermark** definition and the **Lateness Threshold** control how the system handles events that are significantly delayed.

*   **Watermark Strategy**: The W is often set with a bounded out-of-orderness delay (L) (e.g., W = Max Observed Event Time - L). This delay L is a safety margin that gives delayed events time to arrive before W commits the results.
*   **Late Event Policy**:
    *   An event is **Late** if **EventTime < Current Watermark**.
    *   An event is **Too Late** if **EventTime < (Current Watermark - Lateness Threshold)**.
*   **Resolution**: Events that are **Too Late** are handled based on policy:
    *   **Discarded**: If the latency/memory cost is too high.
    *   **DLQ**: Sent to a separate stream for retrospective analysis.

This dynamic system forces a core trade-off:

*   **Large L (High Lateness Tolerance)**: Higher confidence in correctness, but higher latency (must wait longer for W to advance) and higher memory usage (buffer must hold more events).
*   **Small L (Low Lateness Tolerance)**: Lower latency, but higher risk of dropping or missing late events, potentially leading to incorrect pattern matches.
