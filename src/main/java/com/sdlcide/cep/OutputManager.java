package com.sdlcide.cep;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;

public class OutputManager {

    private static final Logger LOGGER = LoggerFactory.getLogger(OutputManager.class);

    private final List<Match> emittedMatches = new ArrayList<>();

    public void emitMatch(Match match) {
        LOGGER.info("Pattern match found: {}", match);
        emittedMatches.add(match);
    }

    public List<Match> getEmittedMatches() {
        return emittedMatches;
    }

    public void clear() {
        emittedMatches.clear();
    }
}
