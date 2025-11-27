---
title: Event Streaming Layer for SDLC_IDE
status: Accepted
date: 2025-11-27
authors: Architecture Team (via Yumin@Chen.Software)
project: SDLC_IDE
---

# ADR-002: Event Streaming Layer for SDLC_IDE

## 1. Decision
Adopt a robust event streaming layer (Kafka/Pulsar/NATS style) as the authoritative observable bus for SDLC_IDE. The stream is publish‑only for agents (producers) and subscribe for analytics, indexing, and optional orchestrator consumers. The event layer is observability-first — it records immutable events that describe document lifecycle actions, agent interactions, vectorization updates, and system state transitions. The event system does not replace the DAG’s directed agent-to-agent calls; it merely observes and enables analytics, ML, personalization, and replayable processing.

## 2. Context
SDLC_IDE is a Hybrid Directed Graph Architecture (DAG core + selective mesh) with an orchestrator enforcing allowed edges.
Agents perform directed actions (e.g., PRM → TSM) and must do so via orchestrator rules.
The platform needs:
- end‑to‑end observability and audit trails,
- data for ML/embedding pipelines,
- the ability to replay past events (for rebuilds, debugging, and ML training),
- scalable, low‑latency notifications for UI and downstream systems.

## 3. Rationale
- **Immutability & auditability:** append‑only events provide tamper‑evident history for compliance and debugging.
- **Decoupling:** producers don’t need to know about consumers (analytics, KBA, model trainers).
- **Replayability:** supports rebuilding vector indexes, retraining models, or reconstructing state after incidents.
- **Scalability:** mature streaming systems scale to high QPS and large retention.
- **Observability feed:** gives the KBA and analytics engines the signals needed for blind‑spot detection, personalization, and usage metrics.
- **Safety:** does not circumvent DAG rules — all agent-to-agent commands must still be authorized by orchestrator.

## 4. Consequences
**Positive**
- Clear, immutable event history for each document and agent action.
- Enables ML pipelines (training data, model input), semantic index updates, and dashboards.
- Provides reliable notification mechanism to UI/IDE and watchers.
- Facilitates safe replay for recovery and testing.

**Negative / Tradeoffs**
- Operational complexity: managing Kafka/Pulsar clusters or using managed providers.
- Storage costs if retention windows are large; needs retention policy discipline.
- Potential data privacy risk if events include sensitive content — must redact PII and sensitive payloads before publishing.
- Latency/ordering considerations across partitions require careful topic design for causal flows.

## 5. Event Layer Contract (core rules)
- **Publish‑only by Agents:** Agents publish events describing actions they took (or were requested to take). Events MUST NOT be used as authorization to perform actions; the orchestrator is the authority.
- **Minimize payloads:** Events should contain references (IDs, hashes, pointers) to documents and not full document bodies unless necessary and permitted by policy.
- **Immutable & versioned schemas:** Event schemas are versioned (v1, v2, …). Producers must include schema_version. All event schema changes must be backward-additive only (no removals). Consumers must ignore unknown fields.
- **Namespaces & ACLs:** Topics are namespaced by project and optionally by environment (e.g., sdlc:project-phi:events). Consumers and producers are authorized by the orchestrator / IAM.
- **Retention / Archival:** Short retention for hot streams (days-weeks); longer archival (cold storage) for compliance via sink connectors.
- **Observability events only:** The streaming bus is observational. Commands that change system state must be passed via orchestrator-authorized agent calls; events can inform orchestrator policy but cannot bypass it.

## 6. Core event types (canonical examples)
Minimal, reference-heavy events. Include project, namespace, actor, trace_id, ts, schema_version.

**PRD_Updated.v1**
```json
{
  "type": "PRD_Updated",
  "schema_version": "v1",
  "ts": "2025-11-27T00:00:00Z",
  "project": "project-phi",
  "prdid": "PRD-042",
  "author": "yumin731598",
  "commit_hash": "a1c9f...",
  "delta_hash": "d3f9e...",
  "required_checks": ["tsd_sync"],
  "meta": { "visibility": "internal", "sensitivity": "low" }
}
```

**TSD_Updated.v1**
```json
{
  "type": "TSD_Updated",
  "schema_version": "v1",
  "ts": "...",
  "project": "...",
  "tsdid": "TSD-042",
  "artifact_paths": ["openapi/v1/payments.json"],
  "canonical_hash": "...",
  "change_summary": "added endpoint /authorize"
}
```

**Artifact_Vectorized.v1**
```json
{
  "type": "Artifact_Vectorized",
  "schema_version": "v1",
  "ts": "...",
  "artifact_id": "openapi/...#endpoint/authorize",
  "vector_id": "vec-9876",
  "metadata": { "component": "payments", "commit": "..." }
}
```

**Agent_Call.v1** (observability of agent-to-agent calls)
```json
{
  "type": "Agent_Call",
  "schema_version": "v1",
  "ts": "...",
  "from": "PRM",
  "to": "TSM",
  "action": "request-tsd-check",
  "call_trace": "trace-xxx",
  "status": "enqueued|success|failed"
}
```
Include additional domain events as needed (BlindSpot_Detected, Impact_Summary, Git_Commit, Policy_Violation).

## 7. Topic and partition design
- **Topic granularity:** Use a balance — too many topics ≈ operational overhead; too few topics ≈ ordering/partitioning headaches. Suggested baseline:
    - `sdlc.{project}.lifecycle` — PRD/TSD/ADR lifecycle events
    - `sdlc.{project}.vector` — vectorization updates
    - `sdlc.{project}.agent-calls` — observability of calls
    - `sdlc.global.policy` — orchestrator/policy events
- **Partitioning key:** Use `artifact_id` as the partition key to ensure that all events for a given artifact are processed in order.
- **Consumer groups:** analytics, KBA ingestion workers, embedding update workers, UI notification workers.

### Required vs. Optional Consumers

| Consumer      | Required? | Purpose            |
|---------------|:---------:|--------------------|
| Vectorizer    | ✅ Required | Embedding updates  |
| KBA Indexer   | Optional  | Knowledge base     |
| UI Notifier   | Optional  | Frontend           |
| Analytics     | Optional  | Metrics            |

### Causal Ordering and Topic Design

To ensure causal ordering, the following principles will be applied:
-   **Partitioning:** As stated above, using `artifact_id` as the partition key guarantees that all events related to a specific artifact (e.g., `PRD-042`) are delivered to a single consumer in the order they were produced.
-   **Explicit Dependencies:** When one artifact depends on another (e.g., a TSD depends on a PRD), the orchestrator will emit an explicit `Dependency_Evaluated` event to signal the relationship.
-   **Rollbacks:** An optional `Rollback_Requested` event type will be introduced to handle cases where a change needs to be reverted.

## 8. Retention, archival & compliance
- **Hot retention:** 7–30 days (depends on activity) to support near-term replay and UI features.
- **Cold archival:** daily sink to object storage (S3) using compacted or chunked files for long-term retention (years) for compliance and audit. Keep event indexes for quick lookup.
- **Compaction:** for topics that track latest state per key (e.g., artifact.latest), enable compacted topics.
- **Encryption & access control:** encrypt in transit and at rest; use tokenized ACLs per namespace.

## 9. Security & privacy
- **PII / secrets:** redact or hash sensitive fields before publish. If event must include sensitive content, store encrypted payloads in object store and place only pointer+access-controls in the event.
- **Auth:** mTLS and IAM-based authentication for producers/consumers. Orchestrator issues tokens.
- **Audit trail:** every publish must include actor, trace_id, and signed_token for non-repudiation (where required).
- **Policy events:** publish Policy_Violation when unauthorized/denied action is attempted.

## 10. Reliability, SLA & scaling
- **Availability SLA:** 99.95% for core event delivery (adjust per infra constraints).
- **Throughput targets and scaling:** plan for burst‑ready clusters; autoscaling for consumers (Kubernetes + consumer group scaling).
- **Backpressure & dead-lettering:** Consumers must have DLQ topics; failing events flow to DLQ with metadata for diagnostics. The DLQ is for manual replay only (operator-driven), and a CLI command will be provided in the PoC for this purpose.
- **Ordering guarantees:** Only guaranteed per partition/key. Design producers/consumers around this.

## 11. Replays & materialized views
- **Replay use cases:** rebuild vector DB, recompute KB, retrain models, reconstruct a document’s history.
- **Idempotency:** consumers must handle idempotent processing (include event event_id).
- **Materialized views:** downstream services (e.g., graph DB, vector DB) consume events and maintain local state; they are the system of record for their domain.

## 12. Connectors & integration
- **Source connectors:** Git webhooks → event producers (VCA publishes Git_Commit events).
- **Sink connectors:** object storage (archive), vector DB (via ingestion workers), graph DB (lineage updates), observability systems.
- **Managed options:** evaluate managed Kafka (Confluent), Pulsar (streaming + topics), or cloud alternatives (AWS MSK, Google Pub/Sub + Dataflow) based on TCO.

## 13. Monitoring & observability
- **Track:** publish rates, consumer lag, consumer error rates, DLQ size, per‑topic throughput, end‑to‑end lag.
- **Dashboards:** per project topic health, per consumer group lag, error heatmaps.
- **Alerts:** consumer lag > threshold, DLQ growth, policy violations events.

## 14. Governance & policy integration
- **Event schemas** versioned and centrally stored (schema registry).
- **Orchestrator** may subscribe to events for auditing but never acts exclusively based on events. Commands must still come through DAG-authorized calls.
- **Policy changes** must be emitted as Policy_Updated events.

## 15. Alternatives considered
- **Lightweight webhook bus:** simpler but lacks replayability, decoupling, scale. Rejected.
- **Centralized DB as event log:** slower, less scalable and harder to stream to many consumers. Rejected.
- **Full-managed serverless pub/sub only:** viable for smaller scale but may not provide topic partitioning/control needed for ordering/keyed replay in large deployments. Considered acceptable as an initial PoC.

## 16. Implementation checklist (practical)
- [ ] Choose streaming platform (PoC: Kafka or Pulsar; for fast start: managed Kafka MSK or Confluent Cloud).
- [ ] Define topic naming conventions and partitions.
- [ ] Implement schema registry & event versioning policy.
- [ ] Implement minimal producers: PRM, TSM, VCA (emit lifecycle events).
- [ ] Implement ingestion workers: vectorizer, KBA indexer (consume TSD_Updated & Artifact_Vectorized).
- [ ] Implement DLQ and retries.
- [ ] Add sink connector to archival storage (daily).
- [ ] Integrate monitoring (Prometheus metrics exporter) and dashboards.
- [ ] Define retention & archival policy; implement automated archival cron.
- [ ] Redaction & PII policy enforcement in producer libraries.
- [ ] Document operational runbooks for incident recovery and event replay.

## 17. Next steps & recommended PoC
PoC stack: Kafka (local dev via Docker), Schema Registry (Confluent OSS), consumer group for vectorizer (Python), KBA ingestion worker (Python), and simple UI notifier (WebSocket consumer).
Implement three events (PRD_Updated, TSD_Updated, Artifact_Vectorized) and confirm end‑to‑end replay to rebuild vector index for one demo project.

## 18. Acceptance criteria
- Events for PRD/TSD/Artifact vectorization produced and consumable within 2s in normal load.
- Consumer lag under threshold (< 30s) under defined QPS.
- Successful replay of events over a 7‑day retention window to rebuild vector index.
- Schema registry in place and producers/consumers validate schema on publish/consume.
- PII redaction policy enforced in at least one producer.
