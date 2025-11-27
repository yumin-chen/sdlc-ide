package com.sdlcide.cep;

import java.nio.ByteBuffer;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

public class Event {
    private final UUID eventId;
    private final ByteBuffer key;
    private final long eventTime;
    private final long ingestionTime;
    private final String type;
    private final Map<String, Object> payload;

    public Event(ByteBuffer key, String type, long eventTime, Map<String, Object> payload) {
        this.eventId = UUID.randomUUID();
        this.key = key;
        this.type = type;
        this.eventTime = eventTime;
        this.ingestionTime = System.currentTimeMillis();
        this.payload = payload;
    }

    public UUID getEventId() { return eventId; }
    public ByteBuffer getKey() { return key; }
    public String getType() { return type; }
    public long getEventTime() { return eventTime; }
    public long getIngestionTime() { return ingestionTime; }
    public Map<String, Object> getPayload() { return payload; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Event event = (Event) o;
        return eventId.equals(event.eventId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(eventId);
    }

    @Override
    public String toString() {
        return "Event{" +
                "eventId=" + eventId +
                ", key=" + new String(key.array()) +
                ", eventTime=" + eventTime +
                ", type='" + type + '\'' +
                '}';
    }
}
