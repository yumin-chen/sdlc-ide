package com.sdlcide.cep;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.ByteBuffer;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.concurrent.ConcurrentHashMap;

public class TemporalBuffer {

    private static final Logger LOGGER = LoggerFactory.getLogger(TemporalBuffer.class);

    private final Map<ByteBuffer, PriorityQueue<Event>> buffers;
    private final Watermark watermark;
    private final long maxOutOfOrderness;
    private long maxEventTime;

    public TemporalBuffer(Duration maxOutOfOrderness) {
        this.buffers = new ConcurrentHashMap<>();
        this.maxOutOfOrderness = maxOutOfOrderness.toMillis();
        this.watermark = new Watermark(Long.MIN_VALUE + this.maxOutOfOrderness);
        this.maxEventTime = Long.MIN_VALUE;
    }

    public List<Event> ingest(Event event) {
        buffers.computeIfAbsent(event.getKey(), k -> new PriorityQueue<>(Comparator.comparingLong(Event::getEventTime)))
               .add(event);
        maxEventTime = Math.max(maxEventTime, event.getEventTime());
        LOGGER.debug("Ingested event: {}. New maxEventTime: {}", event, maxEventTime);
        return maybeAdvanceWatermark();
    }

    private List<Event> maybeAdvanceWatermark() {
        long newWatermarkValue = maxEventTime - maxOutOfOrderness;
        long oldWatermarkValue = watermark.getCurrentWatermark();

        if (newWatermarkValue > oldWatermarkValue) {
            watermark.advance(newWatermarkValue);
            LOGGER.info("Watermark advanced from {} to {}", oldWatermarkValue, newWatermarkValue);
            return releaseEvents();
        }
        return Collections.emptyList();
    }

    private List<Event> releaseEvents() {
        long currentWatermark = watermark.getCurrentWatermark();
        List<Event> eventsToProcess = new ArrayList<>();

        for (PriorityQueue<Event> queue : buffers.values()) {
            while (!queue.isEmpty() && queue.peek().getEventTime() <= currentWatermark) {
                eventsToProcess.add(queue.poll());
            }
        }

        if (!eventsToProcess.isEmpty()) {
            eventsToProcess.sort(Comparator.comparingLong(Event::getEventTime));
            LOGGER.debug("Releasing {} events for processing", eventsToProcess.size());
        }
        return eventsToProcess;
    }

    public long getCurrentWatermark() {
        return watermark.getCurrentWatermark();
    }
}
