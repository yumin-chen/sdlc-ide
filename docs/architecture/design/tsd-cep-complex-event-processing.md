# TSD-CEP: Complex Event Processing Technical Specification

**Status:** Draft
**Date:** 2025-11-27
**Authors:** System Architecture Team
**Scope:** sdlc-ide CEP subsystem

---

## 1. Purpose

This document provides the **detailed technical specification** for the Complex Event Processing (CEP) subsystem.
It covers event-time semantics, NFA-based pattern matching, buffering, state retention, late-event handling, observability, testing, and operational behavior.

> This TSD complements [ADR-001](./adr-001-complex-event-processing-engine.md), which defines the high-level architectural decision.

---

## 2. System Overview

- **Pattern engine:** NFA-based
- **Time model:** event-time with watermarks
- **Out-of-order tolerance:** configurable lateness windows
- **State model:** per-NFA-instance keyed state
- **Operational model:** metrics, logging, DLQ, resource monitoring

---

## 3. NFA Lifecycle

1. **Creation:** A new NFA instance is created when an event matches a pattern's start condition.
2. **Advancement:** The instance's state progresses as subsequent events in the sequence are matched.
3. **Match emission:** A `Match` is emitted when the instance reaches a final state.
4. **Eviction:** State is discarded when the watermark surpasses the NFA's temporal window or if memory pressure requires it.

**Partitioning:** NFAs are partitioned by a key (e.g., `userId`) for deterministic evaluation within a given partition.

---

## 4. Event Processing

- **Event ingestion:** Events must carry an `event_time`. If a source watermark is absent, the engine will compute a local watermark using heuristics.
- **Buffering:** Events are held in a temporal buffer until `event_time ≤ watermark + lateness`.
- **Late-event classification:**
  - **On-time:** Processed normally.
  - **Recoverable late:** Processed, marked as late, and may optionally emit retractions for previously emitted matches.
  - **Too-late:** Routed to a Dead Letter Queue (DLQ), with a corresponding metric incremented.

---

## 5. Watermark & Lateness

- **Watermark propagation:** Watermarks should be propagated from upstream sources whenever possible. If not available, they will be computed locally based on observed event times.
- **Lateness window:** Configurable per pattern (default: 30s).
- **Recovery window (optional):** An additional configurable time window for late-but-recoverable events.

---

## 6. Late-event Policy

| Category                 | Condition                                  | Action                                               |
|---------------------------|--------------------------------------------|-----------------------------------------------------|
| On-time                   | event_time ≤ watermark + lateness         | Normal processing                                   |
| Recoverable late          | watermark + lateness < event_time ≤ watermark + lateness + recovery_window | Process, mark late, emit optional retractions, log, increment metrics |
| Too-late                  | event_time > watermark + lateness + recovery_window | Route to DLQ, log, increment metric               |

---

## 7. Observability & Metrics

**Metrics to expose:**

- `cep.events.ingested_total` (labels: stream, partition)
- `cep.events.on_time` / `cep.events.late` / `cep.events.too_late`
- `cep.nfa.instances_active` (labels: pattern)
- `cep.buffer.size_bytes` (per partition)
- `cep.state.size_bytes` (per worker)
- `cep.matches.emitted_total` (labels: pattern)
- `cep.evictions.total`
- `cep.dlq.events_total`

**Logs:**

- INFO for late events
- WARN for buffer/memory pressure
- ERROR for DLQ write failures
- Tracing: A trace span should be created for each event and match emission.

**Alerts:**

- Buffer memory > 80% of configured budget.
- Sustained high `too_late` rate.
- Rapid growth of `nfa.instances_active`, indicating a potential state explosion.

---

## 8. State Retention & Eviction

- **Retention:** NFA state is retained until the watermark passes its temporal window plus a configurable guard period (default 1s).
- **Eviction policy:** Primarily time-based, with an optional LRU (Least Recently Used) fallback.
- **Emergency shedding mode:** The engine may drop the oldest NFA instances if memory limits are exceeded.
- **Memory budgets:** Default 512 MB per worker; per-NFA instance soft limit of 128 KB.

---

## 9. Retractions

- Retractions are optional and configured on a per-pattern basis.
- Revisions to prior matches may be emitted for late events that fall within the recoverable window.
- This is an expensive operation and should only be enabled for patterns where correctness requires it.

---

## 10. Testing Strategy

**Unit Tests:**

- In-order events for simple sequences
- State transitions & termination

**Property Tests:**

- Invariants: ensure no false positives are generated.
- Correct progression for all sequence operators.

**Out-of-Order Tests:**

- Late events within the lateness window.
- Too-late events routed to the DLQ.
- Correctness of retractions.

**Watermark Progression Tests:**

- Slow & fast watermark advancement.
- Multiple partitions with different watermark characteristics.

**Integration Tests:**

- End-to-end with a real ingestion source.
- Scenarios with and without source watermarks.

**Stress Tests:**

- High-throughput load.
- Memory consumption under peak load.

**Chaos Tests:**

- Partition lag.
- Node restarts.
- Network jitter.

---

## 11. Versioning & Replay

- Pattern definitions are versioned.
- Replays of event streams are supported to recompute matches with new pattern versions.
- Replays must be controlled, with options for dry-runs, and must be idempotent.

---

## 12. Non-Functional Requirements

- **Throughput**: 50k events/sec per shard (tuneable).
- **Latency**: p99 < 250ms for in-order events.
- **Lateness window**: Default 30s, configurable per pattern.
- **Memory**: 512 MB per worker, max state retention of 24 hours.
- **Availability**: The system should degrade gracefully with backpressure under heavy load.

---

## 13. Diagrams

> Use separate Mermaid/sequence diagrams to illustrate:
- NFA lifecycle
- Buffer & watermark progression
- Late-event classification

---

## 14. Risks & Mitigation

- **State explosion:** Mitigated by per-key limits, aggressive eviction, and throttling.
- **Latency spikes:** Mitigated by monitoring watermark lag and scaling resources accordingly.
- **Operational complexity of retractions:** Mitigated by limiting this feature to critical patterns and documenting its cost.
