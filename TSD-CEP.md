# TSD-CEP: Complex Event Processing Technical Specification

**Status:** Draft
**Date:** 2025-11-27
**Authors:** System Architecture Team (via Yumin Chen)
**Scope:** sdlc-ide CEP subsystem

---

## 1. Purpose

This document provides the **detailed technical specification** for the Complex Event Processing (CEP) subsystem.
It covers event-time semantics, NFA-based pattern matching, buffering, state retention, late-event handling, observability, testing, and operational behavior.

> This TSD complements the ADR, which only defines the high-level architectural decision.

---

## 2. System Overview

- **Pattern engine:** NFA-based
- **Time model:** event-time with watermarks
- **Out-of-order tolerance:** configurable lateness windows
- **State model:** per-NFA-instance keyed state
- **Operational model:** metrics, logging, DLQ, resource monitoring

---

## 3. NFA Lifecycle

1. **Creation:** new NFA instance on pattern start condition.
2. **Advancement:** state progresses on each event arrival.
3. **Match emission:** when final state reached.
4. **Eviction:** remove state when watermark surpasses NFA influence horizon or memory pressure is high.

**Partitioning:** NFAs are partitioned by key for deterministic evaluation within a partition.

---

## 4. Event Processing

- **Event ingestion:** Events must carry `event_time`.
  If source watermark absent, compute local watermark using heuristics.
- **Buffering:** Events buffered until `event_time ≤ watermark + lateness`.
- **Late-event classification:**
  - **On-time:** processed normally.
  - **Recoverable late:** process, mark as late, optionally emit retractions.
  - **Too-late:** route to DLQ, increment metric, log reason.

---

## 5. Watermark & Lateness

- **Watermark propagation:** from upstream sources or local computation.
- **Lateness window:** configurable per pattern (default: 30s).
- **Recovery window (optional):** extra slack for late-but-recoverable events.

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
- Tracing: span per event and match emission

**Alerts:**

- Buffer memory > 80% of configured budget
- Sustained high `too_late` rate
- Rapid growth of `nfa.instances_active`

---

## 8. State Retention & Eviction

- **Retention:** NFA state retained until watermark passes influence horizon + guard period (configurable, default 1s).
- **Eviction policy:** time-based, optional LRU fallback.
- **Emergency shedding mode:** may drop oldest NFA instances if memory limits exceeded.
- **Memory budgets:** default 512 MB per worker; per-NFA instance soft limit 128 KB.

---

## 9. Retractions

- Optional, pattern-specific.
- Revisions to prior matches may be emitted for late events within recoverable window.
- Expensive; only enable for patterns requiring retractions.

---

## 10. Testing Strategy

**Unit Tests:**

- In-order events for simple sequences
- State transitions & termination

**Property Tests:**

- Invariants: no false positives
- Correct progression for all sequence operators

**Out-of-Order Tests:**

- Late events within lateness window
- Too-late events to DLQ
- Retraction correctness

**Watermark Progression Tests:**

- Slow & fast watermark advance
- Multiple partitions

**Integration Tests:**

- End-to-end with real ingestion
- Source watermarks present & absent

**Stress Tests:**

- High-throughput load
- Memory consumption under peak load

**Chaos Tests:**

- Partition lag
- Node restarts
- Network jitter

---

## 11. Versioning & Replay

- Pattern definitions are versioned.
- Replays are supported to recompute matches with new pattern versions.
- Replays must be controlled, optionally dry-run, and idempotent.

---

## 12. Non-Functional Requirements

- Throughput: 50k events/sec per shard (tuneable)
- Latency: p99 < 250ms in-order
- Lateness window: default 30s, configurable
- Memory: 512 MB per worker, max retention 24h
- Availability: degrade gracefully with backpressure

---

## 13. Diagrams

> Use separate Mermaid/sequence diagrams to illustrate:
- NFA lifecycle
- Buffer & watermark progression
- Late-event classification

---

## 14. Risks & Mitigation

- **State explosion:** per-key limits, eviction, throttling.
- **Latency spikes:** monitor watermark lag, scale resources.
- **Operational complexity for retractions:** limit to critical patterns; document cost.

---

## 15. References

- See ADR-CEP.md for architectural decisions and rationale.
- CEP literature: NFA-based engines, watermarks, bounded out-of-order event handling.
