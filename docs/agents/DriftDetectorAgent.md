
---
Agent: DriftDetectorAgent
---

## Responsibility
Detects divergence between the intended design specified in Technical Specification Documents (TSD) and the actual implementation in the codebase. This agent acts as a bridge between the abstract documentation and the concrete reality of the code.

## Input
- **From:** CI/CD Pipeline, Code Repository, and the Event Stream.
- **Via:**
    - Webhooks from the CI/CD pipeline (e.g., on a successful build or test run).
    - Static analysis of the codebase (e.g., on a nightly basis or triggered by a commit).
    - Subscribes to `TSD_Updated.v1` events from the `sdlc.docs.events` topic to stay aware of changes in the technical specifications.

## Output
- **To:** `Governor` Agent and `Notification` Service.
- **Via:** Emits a `Drift_Detected.v1` event to the `sdlc.governance.events` topic.

## Decision Points
- **Drift Threshold:** The agent will use a combination of static analysis tools and heuristics to determine if the code has drifted significantly from the TSD. For example, if the TSD specifies a particular database, and the code is using a different one, that would be a clear case of drift.
- **Automatic Remediation:** In the future, the agent could be configured to take automatic remediation actions, such as rolling back a change or creating a new issue in the issue tracker. For now, it will only notify the relevant stakeholders.

## Failure Modes
- **High False Positives:** The agent might incorrectly flag code as drifting from the TSD. This can be mitigated by fine-tuning the static analysis rules and providing a mechanism for users to mark findings as false positives.
- **Incomplete Code Analysis:** The agent might not be able to analyze all aspects of the codebase, leading to missed drift. This can be addressed by integrating with a variety of static analysis tools and linters.

## State Machine
1. `IDLE`: The agent is waiting for a trigger (e.g., a CI/CD webhook or a scheduled analysis).
2. `ANALYZING_CODE`: The agent is performing static analysis of the codebase.
3. `COMPARING_WITH_TSD`: The agent is comparing the results of the code analysis with the relevant TSDs.
4. `REPORTING_DRIFT`: If drift is detected, the agent emits a `Drift_Detected.v1` event.

## Embedding/Semantic Role
- The `DriftDetectorAgent` can use embeddings to perform a more nuanced comparison between the TSD and the code. For example, it could compare the embedding of a TSD section describing an algorithm with the embedding of the code that implements it. This would allow it to detect drift even if the code is not a direct translation of the TSD.

## Dependencies
- **CI/CD Pipeline:** To receive triggers for code analysis.
- **Code Repository:** To access the source code.
- **Static Analysis Tools:** To perform the analysis of the codebase.
- **TraceabilityAgent:** To find the relevant TSD for a given piece of code.
