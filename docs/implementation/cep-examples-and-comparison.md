# CEP Implementation Guide: Examples and Comparison

This guide provides practical examples and a comparative analysis of modern Complex Event Processing (CEP) engines. It serves as a companion to [ADR-001: Complex Event Processing Engine](../architecture/design/adr-001-complex-event-processing-engine.md) and is best read alongside the [CEP Internal Mechanics: A Deep Dive](./cep-internal-mechanics.md) for a full understanding of the underlying principles.

## 1. NFA Lifecycle with Watermarks & Temporal Buffer

The following diagram visualizes the fundamental flow of events from out-of-order ingestion through to NFA processing and instance eviction. For a more detailed, end-to-end lifecycle diagram, see ADR-001.

```mermaid
flowchart TD
    A[Raw Events (Out-of-Order)] --> B[Temporal Buffer (Sort by Event Time)]
    B --> C{Watermark Advances?}
    C -->|Yes| D[Release events in Event Time order]
    C -->|No| B
    D --> E{Does event start a new NFA instance?}
    E -->|Yes| F[Create NFA Instance]
    E -->|No| G[Feed event to existing instances]
    F --> G
    G --> H{Does instance reach FINAL state?}
    H -->|Yes| I[Emit Match]
    H -->|No| J[Still partial match → wait for more events / timers]
    I --> K[Apply Consumption Policy (SKIP_TO_NEXT, SKIP_PAST_LAST, etc.)]
    J --> L{Temporal constraint / timer?}
    L -->|Yes| M[Schedule Event-Time Timer]
    L -->|No| G
    M --> N{Watermark passes timer?}
    N -->|Yes| O[Timeout → Evict Instance]
    N -->|No| J
    D --> P{Event too late?}
    P -->|Yes| Q[Drop or route to DLQ]
    P -->|No| E
```

## 2. Working CEP Examples

### A. Flink CEP (Java)

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

DataStream<Event> input = env
    .fromSource(eventSource, WatermarkStrategy
        .<Event>forBoundedOutOfOrderness(Duration.ofSeconds(5))
        .withTimestampAssigner((event, ts) -> event.getTimestamp()),
    "EventSource");

Pattern<Event, ?> pattern = Pattern.<Event>begin("A")
    .where(e -> e.getType().equals("LOGIN"))
    .followedBy("B")
    .where(e -> e.getType().equals("PAGE_VIEW"))
    .oneOrMore()
    .within(Time.minutes(5));

PatternStream<Event> patternStream = CEP.pattern(input.keyBy(Event::getUserId), pattern);

DataStream<PatternMatchResult> matches = patternStream.select(map -> {
    Event a = map.get("A").get(0);
    List<Event> bList = map.get("B");
    return new PatternMatchResult(a, bList);
});
```

**Notes:**
*   `keyBy(Event::getUserId)` → per-key NFAs
*   `WatermarkStrategy.forBoundedOutOfOrderness` → handles late/out-of-order events
*   `oneOrMore()` → may spawn multiple NFA instances per key

### B. ksqlDB (Kafka Streams CEP)

```sql
CREATE STREAM logins (userId STRING, eventType STRING, ts BIGINT)
  WITH (KAFKA_TOPIC='events', VALUE_FORMAT='JSON', TIMESTAMP='ts');

CREATE TABLE user_sessions AS
  SELECT userId,
         COUNT(*) AS pageViews
  FROM logins
  WINDOW TUMBLING (SIZE 5 MINUTES, GRACE PERIOD 30 SECONDS)
  WHERE eventType = 'PAGE_VIEW'
  GROUP BY userId
  EMIT CHANGES;
```

**Notes:**
*   Kafka Streams uses event-time windows + grace periods for out-of-order handling.
*   Overlapping patterns are handled via windowed aggregation.
*   No explicit NFA API, but the underlying Streams library uses similar partial-match logic internally.

### C. Apache Beam (Java)

```java
PCollection<Event> events = pipeline
    .apply("ReadEvents", KafkaIO.read(...))
    .apply("AssignTimestamps", WithTimestamps.of(Event::getTimestamp))
    .apply("Watermarks", WatermarkStrategies.forBoundedOutOfOrderness(Duration.ofSeconds(5)));

PCollection<PatternMatchResult> matches = CEP.pattern(events)
    .keyBy(Event::getUserId)
    .begin("A").where(e -> e.getType().equals("LOGIN"))
    .followedBy("B").where(e -> e.getType().equals("PAGE_VIEW"))
    .oneOrMore()
    .within(Duration.ofMinutes(5))
    .select(...);
```

**Notes:**
*   Beam handles event-time & late data via `WatermarkStrategies`.
*   The Pattern API (via Beam’s Patterns / CEP extension) mirrors Flink CEP.

## 3. Flink vs. Kafka Streams vs. Beam: Implementation Comparison

| Feature / Engine                | Flink CEP                               | Kafka Streams                                | Apache Beam                                  |
| ------------------------------- | --------------------------------------- | -------------------------------------------- | -------------------------------------------- |
| **Pattern API**                 | Explicit NFA, `PatternStream`           | Windowed aggregations, KTables, Streams DSL  | Pattern API via CEP extensions               |
| **Event-Time Semantics**        | Full support, watermarks + buffer       | Windows + grace period                       | Watermarks + allowed lateness                |
| **NFA Instances / Partial Matches** | One per key; supports multiple overlapping matches | Implicit via aggregations                  | One per key; supports multiple overlapping matches |
| **Late Event Handling**         | Allowed lateness; retractions optional  | Grace period; late events can be dropped     | Allowed lateness; triggers re-computation or late outputs |
| **Negation / Absence Patterns** | Supported (`NOT` / absence)             | Limited; often requires custom logic         | Supported via CEP extensions                 |
| **Scalability / Partitioning**  | Keyed streams; RocksDB state backend    | Kafka partitions                             | Keyed streams; state backend depends on runner (e.g., Flink runner) |
| **Consumption / Skip Policy**   | `SKIP_TO_NEXT` / `SKIP_PAST_LAST`       | N/A                                          | `SKIP_TO_NEXT` / `SKIP_PAST_LAST`          |
