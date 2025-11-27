package com.sdlcide.cep;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class SharedEventBuffer {
    private final Map<UUID, Event> eventStore;
    private final Map<UUID, Integer> refCounts;

    public SharedEventBuffer() {
        this.eventStore = new ConcurrentHashMap<>();
        this.refCounts = new ConcurrentHashMap<>();
    }

    public void register(Event event) {
        eventStore.put(event.getEventId(), event);
        refCounts.put(event.getEventId(), 1);
    }

    public void addReference(UUID eventId) {
        refCounts.computeIfPresent(eventId, (id, count) -> count + 1);
    }

    public void release(UUID eventId) {
        refCounts.computeIfPresent(eventId, (id, count) -> {
            int newCount = count - 1;
            if (newCount == 0) {
                eventStore.remove(eventId);
                return null; // Remove the entry from refCounts
            }
            return newCount;
        });
    }

    public Event get(UUID eventId) {
        return eventStore.get(eventId);
    }
}
