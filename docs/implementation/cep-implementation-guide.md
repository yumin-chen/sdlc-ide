# Applying CEP Lifecycle to Your Project: Complete Implementation

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Event Ingestion                        │
│  ┌─────────────┐     ┌──────────────┐                   │
│  │  Kafka/     │────▶│  Temporal    │                   │
│  │  Stream     │     │  Buffer      │                   │
│  └─────────────┘     └──────────────┘                   │
└────────────────────────┬─────────────────────────────────┘
                         │ Events in EventTime order
                         ▼
┌──────────────────────────────────────────────────────────┐
│                 NFA Instance Manager                      │
│  ┌────────────┐  ┌──────────────┐  ┌────────────┐      │
│  │ Instance   │  │ Event-Time   │  │ State      │      │
│  │ Registry   │  │ Timer Svc    │  │ Store      │      │
│  └────────────┘  └──────────────┘  └────────────┘      │
└────────────────────────┬─────────────────────────────────┘
                         │ Completed matches
                         ▼
┌──────────────────────────────────────────────────────────┐
│              Output & Late Event Handler                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐     │
│  │  Match      │  │  Retraction  │  │    DLQ     │     │
│  │  Emitter    │  │  Handler     │  │  (Late)    │     │
│  └─────────────┘  └──────────────┘  └────────────┘     │
└──────────────────────────────────────────────────────────┘
```

## 1. Core Components Implementation

### A. Event Model

```java
public class Event {
    private final String id;
    private final String type;
    private final long eventTime;       // Microseconds since epoch
    private final long ingestionTime;   // System arrival time
    private final byte[] partitionKey;  // For state partitioning
    private final Map<String, Object> attributes;

    // Ordering by eventTime for temporal buffer
    public int compareTo(Event other) {
        return Long.compare(this.eventTime, other.eventTime);
    }
}
```

### B. Temporal Buffer with Watermark Management

```java
public class TemporalBuffer {
    private final long maxOutOfOrdernessMs;
    private final Map<ByteBuffer, PriorityQueue<Event>> perKeyBuffers;
    private volatile long currentWatermark;
    private final EventReleaseCallback callback;

    public TemporalBuffer(long maxOutOfOrdernessMs, EventReleaseCallback callback) {
        this.maxOutOfOrdernessMs = maxOutOfOrdernessMs;
        this.perKeyBuffers = new ConcurrentHashMap<>();
        this.currentWatermark = 0;
        this.callback = callback;
    }

    public void ingest(Event event) {
        // Add to per-key buffer
        perKeyBuffers
            .computeIfAbsent(
                ByteBuffer.wrap(event.getPartitionKey()),
                k -> new PriorityQueue<>(Comparator.comparingLong(Event::getEventTime))
            )
            .add(event);

        // Try to advance watermark
        advanceWatermark();
    }

    private void advanceWatermark() {
        // Watermark = min(all buffer heads) - maxOutOfOrderness
        long minEventTime = perKeyBuffers.values().stream()
            .filter(queue -> !queue.isEmpty())
            .mapToLong(queue -> queue.peek().getEventTime())
            .min()
            .orElse(Long.MAX_VALUE);

        long newWatermark = minEventTime - maxOutOfOrdernessMs;

        if (newWatermark > currentWatermark) {
            currentWatermark = newWatermark;
            releaseEvents();
        }
    }

    private void releaseEvents() {
        // Release all events with eventTime <= watermark
        perKeyBuffers.forEach((key, queue) -> {
            while (!queue.isEmpty() &&
                   queue.peek().getEventTime() <= currentWatermark) {
                Event event = queue.poll();
                callback.onEventRelease(event);
            }
        });
    }

    public long getCurrentWatermark() {
        return currentWatermark;
    }
}
```

### C. NFA Instance State

```java
public class NFAInstance {
    private final UUID instanceId;
    private final String patternKey;  // e.g., "user123"
    private NFAState currentState;
    private final List<Long> matchedEventIds;  // References to SharedEventBuffer
    private final long startTime;
    private final long expiryTime;
    private final Map<String, Object> aggregations;

    public NFAInstance(Event startEvent, NFAState initialState, long timeoutMs) {
        this.instanceId = UUID.randomUUID();
        this.patternKey = new String(startEvent.getPartitionKey());
        this.currentState = initialState;
        this.matchedEventIds = new ArrayList<>();
        this.startTime = startEvent.getEventTime();
        this.expiryTime = startTime + timeoutMs;
        this.aggregations = new HashMap<>();
    }

    public boolean isExpired(long watermark) {
        return watermark >= expiryTime;
    }

    public boolean canAccept(Event event) {
        return currentState.getPredicate().test(event);
    }

    public TransitionResult advance(Event event, SharedEventBuffer buffer) {
        if (!canAccept(event)) {
            return TransitionResult.rejected();
        }

        // Add event reference
        long eventId = buffer.register(event);
        matchedEventIds.add(eventId);

        // Check for branching (greedy patterns)
        if (currentState.getQuantifier() == Quantifier.ONE_OR_MORE) {
            // Create branch that stays in current state
            NFAInstance branch1 = this.clone();

            // Create branch that moves to next state
            NFAInstance branch2 = this.clone();
            branch2.currentState = currentState.getNextState();

            return TransitionResult.branched(branch1, branch2);
        }

        // Normal transition
        currentState = currentState.getNextState();

        if (currentState.isFinal()) {
            return TransitionResult.completed(this);
        }

        return TransitionResult.advanced(this);
    }
}
```

### D. Event-Time Timer Service

```java
public class EventTimeTimerService {
    // Sorted by expiry time
    private final TreeMap<Long, Set<UUID>> timers;
    private final NFAInstanceRegistry registry;

    public EventTimeTimerService(NFAInstanceRegistry registry) {
        this.timers = new TreeMap<>();
        this.registry = registry;
    }

    public void registerTimer(UUID instanceId, long expiryTime) {
        timers.computeIfAbsent(expiryTime, k -> new HashSet<>())
              .add(instanceId);
    }

    public void checkTimers(long watermark) {
        // Fire all timers with expiryTime <= watermark
        var expiredTimers = timers.headMap(watermark, true);

        for (var entry : expiredTimers.entrySet()) {
            long expiryTime = entry.getKey();
            Set<UUID> instanceIds = entry.getValue();

            for (UUID id : instanceIds) {
                NFAInstance instance = registry.getInstance(id);
                if (instance != null) {
                    handleTimeout(instance, expiryTime, watermark);
                }
            }
        }

        // Remove fired timers
        expiredTimers.clear();
    }

    private void handleTimeout(NFAInstance instance, long expiryTime, long watermark) {
        // Emit timeout event or absence pattern
        TimeoutEvent timeout = new TimeoutEvent(
            instance.getInstanceId(),
            instance.getPatternKey(),
            expiryTime,
            watermark,
            instance.getCurrentState()
        );

        // Clean up instance
        registry.evict(instance.getInstanceId());

        // Optionally emit to monitoring
        metrics.recordTimeout(instance);
    }
}
```

### E. NFA Instance Manager (The Core Engine)

```java
public class NFAInstanceManager {
    private final Map<String, Set<NFAInstance>> activeInstances;  // key -> instances
    private final SharedEventBuffer eventBuffer;
    private final EventTimeTimerService timerService;
    private final ConsumptionPolicy policy;
    private final MatchEmitter matchEmitter;

    public void processEvent(Event event) {
        String key = new String(event.getPartitionKey());
        Set<NFAInstance> instances = activeInstances.computeIfAbsent(
            key,
            k -> new HashSet<>()
        );

        Set<NFAInstance> newInstances = new HashSet<>();
        Set<NFAInstance> completedInstances = new HashSet<>();
        Set<NFAInstance> toRemove = new HashSet<>();

        // Try to advance existing instances
        for (NFAInstance instance : instances) {
            TransitionResult result = instance.advance(event, eventBuffer);

            switch (result.getType()) {
                case ADVANCED:
                    // Instance progressed, keep it
                    break;

                case BRANCHED:
                    // Greedy pattern created branches
                    newInstances.addAll(result.getBranches());
                    toRemove.add(instance);  // Replace with branches
                    break;

                case COMPLETED:
                    completedInstances.add(instance);
                    toRemove.add(instance);
                    break;

                case REJECTED:
                    // Event doesn't match, keep instance unchanged
                    break;
            }
        }

        // Remove instances that were replaced/completed
        instances.removeAll(toRemove);

        // Apply consumption policy for completed matches
        applyConsumptionPolicy(completedInstances, instances);

        // Emit completed matches
        for (NFAInstance completed : completedInstances) {
            emitMatch(completed);
        }

        // Try to start new instance from pattern start state
        if (startState.getPredicate().test(event)) {
            NFAInstance newInstance = new NFAInstance(
                event,
                startState,
                patternTimeoutMs
            );
            newInstances.add(newInstance);
            timerService.registerTimer(
                newInstance.getInstanceId(),
                newInstance.getExpiryTime()
            );
        }

        // Add new instances
        instances.addAll(newInstances);
    }

    private void applyConsumptionPolicy(
        Set<NFAInstance> completed,
        Set<NFAInstance> active
    ) {
        if (policy == ConsumptionPolicy.SKIP_TO_NEXT) {
            // Remove all instances that started at or before
            // the first event of any completed match
            long earliestCompletedStart = completed.stream()
                .mapToLong(NFAInstance::getStartTime)
                .min()
                .orElse(Long.MAX_VALUE);

            active.removeIf(inst ->
                inst.getStartTime() <= earliestCompletedStart
            );
        } else if (policy == ConsumptionPolicy.SKIP_PAST_LAST) {
            // Remove instances that share any events with completed matches
            Set<Long> completedEventIds = completed.stream()
                .flatMap(inst -> inst.getMatchedEventIds().stream())
                .collect(Collectors.toSet());

            active.removeIf(inst ->
                inst.getMatchedEventIds().stream()
                    .anyMatch(completedEventIds::contains)
            );
        }
        // NO_SKIP: keep all instances
    }
}
```

### F. Late Event Handler

```java
public class LateEventHandler {
    private final long latenessThresholdMs;
    private final NFAInstanceManager nfaManager;
    private final DeadLetterQueue dlq;

    public void handleLateEvent(Event event, long currentWatermark) {
        long eventTime = event.getEventTime();

        // Check how late the event is
        long lateness = currentWatermark - eventTime;

        if (lateness > latenessThresholdMs) {
            // Too late - drop to DLQ
            dlq.send(new LateEventRecord(
                event,
                currentWatermark,
                lateness,
                "Exceeds lateness threshold: " + latenessThresholdMs + "ms"
            ));

            metrics.recordDroppedLateEvent(lateness);
            return;
        }

        // Within allowed lateness window
        // Find potentially affected instances
        Set<NFAInstance> affected = findAffectedInstances(event);

        if (!affected.isEmpty()) {
            // Retract previous matches that might be invalidated
            Set<Match> toRetract = findMatchesToRetract(affected, event);
            for (Match match : toRetract) {
                matchEmitter.retract(match);
            }

            // Reprocess affected instances with the late event
            for (NFAInstance instance : affected) {
                reprocessInstance(instance, event);
            }
        }

        metrics.recordAcceptedLateEvent(lateness);
    }

    private Set<NFAInstance> findAffectedInstances(Event lateEvent) {
        // Find instances where:
        // startTime <= lateEvent.eventTime <= expiryTime
        String key = new String(lateEvent.getPartitionKey());

        return nfaManager.getInstancesForKey(key).stream()
            .filter(inst ->
                inst.getStartTime() <= lateEvent.getEventTime() &&
                lateEvent.getEventTime() <= inst.getExpiryTime()
            )
            .collect(Collectors.toSet());
    }
}
```

## 2. Putting It All Together: Main Engine Loop

```java
public class CEPEngine {
    private final TemporalBuffer temporalBuffer;
    private final NFAInstanceManager nfaManager;
    private final EventTimeTimerService timerService;
    private final LateEventHandler lateEventHandler;

    public void start() {
        // Create temporal buffer with callback
        this.temporalBuffer = new TemporalBuffer(
            maxOutOfOrdernessMs,
            event -> processInOrder(event)
        );

        // Start watermark advancement thread
        startWatermarkMonitor();
    }

    public void ingest(Event event) {
        long currentWatermark = temporalBuffer.getCurrentWatermark();

        // Check if event is late
        if (event.getEventTime() < currentWatermark) {
            lateEventHandler.handleLateEvent(event, currentWatermark);
        } else {
            // Normal path: add to temporal buffer
            temporalBuffer.ingest(event);
        }
    }

    private void processInOrder(Event event) {
        // This is called by temporal buffer when event is released
        nfaManager.processEvent(event);
    }

    private void startWatermarkMonitor() {
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

        scheduler.scheduleAtFixedRate(() -> {
            long watermark = temporalBuffer.getCurrentWatermark();

            // Fire expired timers
            timerService.checkTimers(watermark);

            // Evict expired instances
            nfaManager.evictExpiredInstances(watermark);

            // Update metrics
            metrics.recordWatermark(watermark);

        }, 0, 100, TimeUnit.MILLISECONDS);
    }
}
```

## 3. Configuration & Trade-offs

```java
public class CEPConfig {
    // Temporal settings
    private long maxOutOfOrdernessMs = 5000;      // 5 seconds
    private long latenessThresholdMs = 2000;       // 2 seconds

    // Pattern settings
    private long patternTimeoutMs = 300000;        // 5 minutes
    private ConsumptionPolicy policy = ConsumptionPolicy.SKIP_PAST_LAST;

    // Memory management
    private long maxMemoryBytes = 2L * 1024 * 1024 * 1024;  // 2GB
    private int maxInstancesPerKey = 1000;

    // Performance tuning
    private int bufferSize = 10000;
    private int checkpointIntervalMs = 60000;      // 1 minute

    /**
     * Trade-off guide:
     *
     * maxOutOfOrderness:
     *   - Larger → more correct (handles more disorder)
     *   - Smaller → lower latency, less memory
     *
     * latenessThreshold:
     *   - Larger → fewer dropped events, more retractions
     *   - Smaller → faster processing, simpler semantics
     *
     * patternTimeout:
     *   - Larger → more complete matches
     *   - Smaller → less memory usage
     */
}
```

## 4. Testing the Lifecycle

```java
@Test
public void testNFALifecycle_WithOutOfOrder() {
    CEPEngine engine = new CEPEngine(new CEPConfig()
        .maxOutOfOrderness(3000)
        .latenessThreshold(2000)
        .patternTimeout(5000)
    );

    // Define pattern: A -> B+ -> C within 5 sec
    Pattern pattern = Pattern.begin("A")
        .where(e -> e.getType().equals("A"))
        .followedBy("B")
        .where(e -> e.getType().equals("B"))
        .oneOrMore()
        .followedBy("C")
        .where(e -> e.getType().equals("C"))
        .within(Duration.ofSeconds(5));

    engine.registerPattern(pattern);

    // Ingest events (some out of order)
    engine.ingest(new Event("E1", "A", 5000, key));
    engine.ingest(new Event("E3", "B", 9000, key));  // Out of order
    engine.ingest(new Event("E2", "B", 7000, key));
    engine.ingest(new Event("E4", "C", 12000, key));

    // Wait for processing
    Thread.sleep(1000);

    // Verify match emitted
    List<Match> matches = engine.getMatches();
    assertEquals(1, matches.size());
    assertEquals(Arrays.asList("E1", "E2", "E3", "E4"),
                 matches.get(0).getEventSequence());
}

@Test
public void testLateEventHandling() {
    CEPEngine engine = new CEPEngine(new CEPConfig()
        .maxOutOfOrderness(3000)
        .latenessThreshold(2000)
    );

    // Ingest events to advance watermark
    engine.ingest(new Event("E1", "A", 5000, key));
    engine.ingest(new Event("E2", "B", 10000, key));

    // Watermark should be at 7000 (10000 - 3000)
    assertEquals(7000, engine.getWatermark());

    // Send late event within threshold
    engine.ingest(new Event("E3", "B", 6000, key));  // 1 sec late

    // Should be processed
    assertEquals(0, engine.getDroppedEvents().size());

    // Send very late event
    engine.ingest(new Event("E4", "B", 4000, key));  // 3 sec late

    // Should be dropped
    assertEquals(1, engine.getDroppedEvents().size());
}
```

## 5. Monitoring & Observability

```java
public class CEPMetrics {
    // Latency metrics
    Histogram eventLatency = ...;           // ingestion - event time
    Histogram processingLatency = ...;       // match emit - event time

    // Throughput
    Counter eventsIngested = ...;
    Counter eventsProcessed = ...;
    Counter matchesEmitted = ...;

    // Quality metrics
    Counter lateEventsAccepted = ...;
    Counter lateEventsDropped = ...;
    Counter retractions = ...;

    // State metrics
    Gauge activeNFAInstances = ...;
    Gauge bufferSize = ...;
    Gauge watermarkLag = ...;              // current time - watermark

    // Performance
    Timer patternEvaluationTime = ...;
    Histogram instanceBranching = ...;      // branches per event
}
```
