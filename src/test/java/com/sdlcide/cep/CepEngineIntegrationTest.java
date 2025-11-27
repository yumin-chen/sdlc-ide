package com.sdlcide.cep;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.nio.ByteBuffer;
import java.time.Duration;
import java.util.Map;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class CepEngineIntegrationTest {

    private CepEngine cepEngine;
    private final ByteBuffer key = ByteBuffer.wrap("user1".getBytes());

    @BeforeEach
    void setUp() {
        Pattern pattern = Pattern.begin("A", e -> e.getType().equals("LOGIN"))
                .followedBy("B", e -> e.getType().equals("PURCHASE"))
                .within(Duration.ofSeconds(10));

        cepEngine = new CepEngine(pattern, Duration.ofSeconds(5));
    }

    @Test
    void testSimpleMatchWithOutOfOrderEvents() {
        // Ingest events out of order
        cepEngine.ingest(new Event(key, "LOGIN", 10000, Map.of()));    // t=10s
        cepEngine.ingest(new Event(key, "OTHER", 12000, Map.of()));   // t=12s
        cepEngine.ingest(new Event(key, "PURCHASE", 15000, Map.of())); // t=15s

        // Watermark is still low, so no events processed yet, and no matches
        assertEquals(0, cepEngine.getOutputManager().getEmittedMatches().size());

        // Ingest an event far in the future to advance the watermark past all buffered events
        cepEngine.ingest(new Event(key, "FLUSH", 30000, Map.of()));   // t=30s

        // Now, the watermark should have advanced, processing the buffered events.
        // The LOGIN at t=10 and PURCHASE at t=15 should form a match within the 10s window.
        assertEquals(1, cepEngine.getOutputManager().getEmittedMatches().size());
        Match match = cepEngine.getOutputManager().getEmittedMatches().get(0);
        assertEquals(2, match.getEvents().size());
        assertEquals("LOGIN", match.getEvents().get(0).getType());
        assertEquals("PURCHASE", match.getEvents().get(1).getType());
    }

    @Test
    void testPatternTimeout() {
        // Ingest a starting event
        cepEngine.ingest(new Event(key, "LOGIN", 10000, Map.of())); // t=10s

        // Ingest an event that does not match
        cepEngine.ingest(new Event(key, "OTHER", 12000, Map.of())); // t=12s

        // Ingest the second event for the pattern, but *after* the 10s window has passed
        cepEngine.ingest(new Event(key, "PURCHASE", 25000, Map.of())); // t=25s

        // Ingest a flush event
        cepEngine.ingest(new Event(key, "FLUSH", 40000, Map.of())); // t=40s

        // The NFA instance for the first LOGIN event should have been evicted by the timer,
        // so no match should be found.
        assertTrue(cepEngine.getOutputManager().getEmittedMatches().isEmpty(), "A match was found when it should have timed out.");
    }
}
