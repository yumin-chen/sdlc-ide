package com.sdlcide.cep;

import java.time.Duration;
import java.util.List;

public class CepEngine {

    private final TemporalBuffer temporalBuffer;
    private final NfaInstanceManager nfaInstanceManager;
    private final SharedEventBuffer sharedEventBuffer;
    private final OutputManager outputManager;

    public CepEngine(Pattern pattern, Duration maxOutOfOrderness) {
        this.outputManager = new OutputManager();
        this.sharedEventBuffer = new SharedEventBuffer();
        this.nfaInstanceManager = new NfaInstanceManager(pattern, sharedEventBuffer, outputManager::emitMatch);
        this.temporalBuffer = new TemporalBuffer(maxOutOfOrderness);
    }

    public void ingest(Event event) {
        List<Event> eventsToProcess = temporalBuffer.ingest(event);

        // Process the entire batch of events first
        for (Event e : eventsToProcess) {
            nfaInstanceManager.processEvent(e);
        }

        // Only then, run eviction logic once with the new watermark
        if (!eventsToProcess.isEmpty()) {
            nfaInstanceManager.evictExpiredInstances(temporalBuffer.getCurrentWatermark());
        }
    }

    public OutputManager getOutputManager() {
        return outputManager;
    }
}
