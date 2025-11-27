package com.sdlcide.cep;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

public class NfaInstance {
    private final UUID instanceId;
    private final State currentState;
    private final List<UUID> matchedEventIds;
    private final long startTime;
    private final long expiryTime;

    public NfaInstance(State startState, Event startEvent, Pattern pattern, SharedEventBuffer buffer) {
        this.instanceId = UUID.randomUUID();
        this.currentState = startState;
        this.matchedEventIds = new ArrayList<>();
        this.matchedEventIds.add(startEvent.getEventId());
        this.startTime = startEvent.getEventTime();
        this.expiryTime = (pattern.getWindow() != null)
                ? this.startTime + pattern.getWindow().toMillis()
                : Long.MAX_VALUE;
        buffer.register(startEvent); // Register the start event
    }

    private NfaInstance(NfaInstance other, State nextState, Event nextEvent, SharedEventBuffer buffer) {
        this.instanceId = other.instanceId; // Branching keeps the same ID for now
        this.currentState = nextState;
        this.matchedEventIds = new ArrayList<>(other.matchedEventIds);
        this.matchedEventIds.add(nextEvent.getEventId());
        this.startTime = other.startTime;
        this.expiryTime = other.expiryTime;
        buffer.register(nextEvent); // Register the new event
        // Add references to all previous events in the sequence
        other.matchedEventIds.forEach(buffer::addReference);
    }

    public NfaInstance advance(State nextState, Event nextEvent, SharedEventBuffer buffer) {
        return new NfaInstance(this, nextState, nextEvent, buffer);
    }

    public NfaInstance stay(Event nextEvent, SharedEventBuffer buffer) {
         return new NfaInstance(this, this.currentState, nextEvent, buffer);
    }

    public UUID getInstanceId() {
        return instanceId;
    }

    public State getCurrentState() {
        return currentState;
    }

    public List<Event> getMatchedEvents(SharedEventBuffer buffer) {
        return matchedEventIds.stream()
                .map(buffer::get)
                .collect(Collectors.toList());
    }

    public List<UUID> getMatchedEventIds() {
        return matchedEventIds;
    }

    public long getStartTime() {
        return startTime;
    }

    public long getExpiryTime() {
        return expiryTime;
    }

    public boolean isExpired(long watermark) {
        return watermark >= this.expiryTime;
    }

    public void releaseEvents(SharedEventBuffer buffer) {
        matchedEventIds.forEach(buffer::release);
    }
}
