package com.sdlcide.cep;

import java.util.List;
import java.util.UUID;

public class Match {
    private final UUID matchId;
    private final List<Event> events;
    private final long processingTime;

    public Match(List<Event> events) {
        this.matchId = UUID.randomUUID();
        this.events = List.copyOf(events);
        this.processingTime = System.currentTimeMillis();
    }

    public UUID getMatchId() {
        return matchId;
    }

    public List<Event> getEvents() {
        return events;
    }

    public long getProcessingTime() {
        return processingTime;
    }

    @Override
    public String toString() {
        return "Match{" +
                "matchId=" + matchId +
                ", events=" + events +
                '}';
    }
}
