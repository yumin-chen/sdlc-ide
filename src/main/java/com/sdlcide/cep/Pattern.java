package com.sdlcide.cep;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Predicate;

public class Pattern {
    private final List<State> states;
    private State currentState;
    private Duration window;
    private final ConsumptionPolicy consumptionPolicy;

    private Pattern(State startState, ConsumptionPolicy consumptionPolicy) {
        this.states = new ArrayList<>();
        this.states.add(startState);
        this.currentState = startState;
        this.consumptionPolicy = consumptionPolicy;
    }

    public static Pattern begin(String name, Predicate<Event> condition) {
        return new Pattern(new State(name, condition), ConsumptionPolicy.SKIP_PAST_LAST_EVENT); // Default policy
    }
     public static Pattern begin(String name, Predicate<Event> condition, ConsumptionPolicy policy) {
        return new Pattern(new State(name, condition), policy);
    }

    public Pattern followedBy(String name, Predicate<Event> condition) {
        State nextState = new State(name, condition);
        currentState.addTransition(nextState);
        states.add(nextState);
        currentState = nextState;
        return this;
    }

    public Pattern oneOrMore() {
        if (currentState != null) {
            currentState.setQuantifier(QuantifierType.ONE_OR_MORE);
        }
        return this;
    }

    public Pattern within(Duration window) {
        this.window = window;
        return this;
    }

    public List<State> getStates() {
        return states;
    }

    public State getStartState() {
        return states.isEmpty() ? null : states.get(0);
    }

    public Duration getWindow() {
        return window;
    }

    public ConsumptionPolicy getConsumptionPolicy() {
        return consumptionPolicy;
    }

    public enum ConsumptionPolicy {
        SKIP_TO_NEXT,
        SKIP_PAST_LAST_EVENT,
        NO_SKIP
    }
}
