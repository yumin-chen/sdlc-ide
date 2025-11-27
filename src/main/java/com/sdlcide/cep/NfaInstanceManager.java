package com.sdlcide.cep;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.ByteBuffer;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;
import java.util.stream.Collectors;

public class NfaInstanceManager {

    private static final Logger LOGGER = LoggerFactory.getLogger(NfaInstanceManager.class);

    private final Pattern pattern;
    private final Map<ByteBuffer, Set<NfaInstance>> activeInstances;
    private final TreeMap<Long, Set<UUID>> timerRegistry;
    private final SharedEventBuffer eventBuffer;
    private final Consumer<Match> downstream;

    public NfaInstanceManager(Pattern pattern, SharedEventBuffer eventBuffer, Consumer<Match> downstream) {
        this.pattern = pattern;
        this.activeInstances = new ConcurrentHashMap<>();
        this.timerRegistry = new TreeMap<>();
        this.eventBuffer = eventBuffer;
        this.downstream = downstream;
    }

    public void processEvent(Event event) {
        Set<NfaInstance> instancesForKey = activeInstances.computeIfAbsent(event.getKey(), k -> new HashSet<>());
        Set<NfaInstance> newInstances = new HashSet<>();
        Set<NfaInstance> completedInstances = new HashSet<>();
        Set<NfaInstance> instancesToRemove = new HashSet<>();

        // 1. Try to advance existing instances
        Set<NfaInstance> instancesToAdvance = new HashSet<>(instancesForKey);
        for (NfaInstance instance : instancesToAdvance) {
            State currentState = instance.getCurrentState();

            if (currentState.getQuantifier() == QuantifierType.ONE_OR_MORE && currentState.matches(event)) {
                newInstances.add(instance.stay(event, eventBuffer));
            }

            for (State nextState : currentState.getTransitions()) {
                if (nextState.matches(event)) {
                    NfaInstance newInstance = instance.advance(nextState, event, eventBuffer);
                    if (isFinalState(nextState)) {
                        completedInstances.add(newInstance);
                    } else {
                        newInstances.add(newInstance);
                    }
                }
            }
        }

        // 2. Try to start a new instance
        State startState = pattern.getStartState();
        if (startState != null && startState.matches(event)) {
            NfaInstance newInstance = new NfaInstance(startState, event, pattern, eventBuffer);
            if (isFinalState(startState)) {
                completedInstances.add(newInstance);
            } else {
                newInstances.add(newInstance);
                registerTimer(newInstance);
            }
        }

        instancesForKey.removeAll(instancesToRemove);
        instancesForKey.addAll(newInstances);

        // 3. Process completed matches and apply consumption policy
        if (!completedInstances.isEmpty()) {
            for (NfaInstance completed : completedInstances) {
                downstream.accept(new Match(completed.getMatchedEvents(eventBuffer)));
            }
            applyConsumptionPolicy(completedInstances, instancesForKey);
        }
    }

    private void applyConsumptionPolicy(Set<NfaInstance> completed, Set<NfaInstance> active) {
        Set<NfaInstance> instancesToRemove;
        switch (pattern.getConsumptionPolicy()) {
            case SKIP_TO_NEXT:
                long firstEventTime = completed.stream()
                        .mapToLong(NfaInstance::getStartTime)
                        .min()
                        .orElse(Long.MAX_VALUE);
                instancesToRemove = active.stream()
                        .filter(inst -> inst.getStartTime() <= firstEventTime)
                        .collect(Collectors.toSet());
                break;
            case SKIP_PAST_LAST_EVENT:
                Set<UUID> completedEventIds = completed.stream()
                        .flatMap(inst -> inst.getMatchedEventIds().stream())
                        .collect(Collectors.toSet());
                instancesToRemove = active.stream()
                        .filter(inst -> inst.getMatchedEventIds().stream().anyMatch(completedEventIds::contains))
                        .collect(Collectors.toSet());
                break;
            case NO_SKIP:
            default:
                instancesToRemove = new HashSet<>();
                break;
        }

        instancesToRemove.forEach(inst -> inst.releaseEvents(eventBuffer));
        active.removeAll(instancesToRemove);
    }

    private boolean isFinalState(State state) {
        return state.getTransitions().isEmpty();
    }

    private void registerTimer(NfaInstance instance) {
        if (instance.getExpiryTime() != Long.MAX_VALUE) {
            timerRegistry.computeIfAbsent(instance.getExpiryTime(), k -> new HashSet<>()).add(instance.getInstanceId());
            LOGGER.debug("Registered timer for instance {} at {}", instance.getInstanceId(), instance.getExpiryTime());
        }
    }

    public void evictExpiredInstances(long watermark) {
        var expiredTimers = timerRegistry.headMap(watermark, true);
        Set<UUID> idsToEvict = new HashSet<>();
        expiredTimers.values().forEach(idsToEvict::addAll);

        if (!idsToEvict.isEmpty()) {
            activeInstances.values().forEach(set ->
                set.removeIf(instance -> {
                    if (idsToEvict.contains(instance.getInstanceId())) {
                        LOGGER.info("Evicting instance {} due to timeout", instance.getInstanceId());
                        instance.releaseEvents(eventBuffer);
                        return true;
                    }
                    return false;
                })
            );
        }
        expiredTimers.clear();
    }
}
