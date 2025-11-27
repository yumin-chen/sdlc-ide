package com.sdlcide.cep;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Predicate;

public class State {
    private final String name;
    private final Predicate<Event> condition;
    private final List<State> transitions;
    private QuantifierType quantifier;

    public State(String name, Predicate<Event> condition) {
        this.name = name;
        this.condition = condition;
        this.transitions = new ArrayList<>();
        this.quantifier = QuantifierType.SINGLE;
    }

    public void addTransition(State target) {
        this.transitions.add(target);
    }

    public String getName() {
        return name;
    }

    public boolean matches(Event event) {
        return condition.test(event);
    }

    public List<State> getTransitions() {
        return transitions;
    }

    public QuantifierType getQuantifier() {
        return quantifier;
    }

    public void setQuantifier(QuantifierType quantifier) {
        this.quantifier = quantifier;
    }
}
