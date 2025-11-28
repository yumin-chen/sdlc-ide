# ADR-PAOS-002: Deterministic Agent Runtime

- **Status**: Proposed
- **Date**: 2025-11-28
- **Deciders**: Yumin Chen

## Context and Problem Statement

Generative AI models (LLMs) are inherently non-deterministic. If used to directly execute tasks or modify files, they can produce unpredictable, incorrect, or even harmful results ("hallucinations"). For a system intended to reliably automate personal and professional workflows, this unpredictability is a significant risk. We cannot build a trustworthy autonomous operating system if its core actions are based on non-deterministic outputs.

We need to design an agent runtime that leverages the creative power of LLMs for drafting while ensuring that all final outputs are safe, correct, and predictable.

## Decision Drivers

- **Reliability**: The system's actions must be repeatable and predictable.
- **Safety**: The system must prevent agents from taking incorrect or destructive actions.
- **Verifiability**: It must be possible to audit and validate an agent's entire workflow, from planning to execution.
- **User Trust**: The user must be confident that the system will not corrupt files, send incorrect messages, or fail silently.
- **Containment of AI**: The creative but unreliable nature of LLMs must be strictly sandboxed.

## Considered Options

1.  **End-to-End Generative Model**: Use a single, powerful LLM to interpret a prompt, plan, and execute the entire task. This is simple to implement but fails all reliability and safety drivers.
2.  **Generative-Deterministic Hybrid Model**: Separate the agent runtime into distinct stages. Use an LLM only for the initial, creative "Draft" stage. All subsequent stages—validation, verification, and execution—must be performed by deterministic, programmatic tools.

## Decision Outcome

Chosen option: **"Generative-Deterministic Hybrid Model"**. The PAOS agent runtime will be a multi-stage pipeline that strictly isolates the non-deterministic LLM.

The canonical pipeline for any agent action will be:
1.  **Parse DSL**: Deterministically parse the structured task definition.
2.  **Plan**: Use static rules or a very small, specialized model to create a high-level plan.
3.  **Draft**: Use a local LLM to generate a *proposed* output (e.g., a code diff, a draft email, a JSON object). This is the only non-deterministic step.
4.  **Validate**: Use deterministic tools to check the draft's correctness (e.g., code linters, AST analysis, schema validation, grammar checkers). If validation fails, the process can loop back to the Draft stage with feedback.
5.  **Verify**: Use a policy engine (OPA) to check the validated draft against user-defined safety and governance rules.
6.  **Emit Output**: Once validated and verified, the final output (e.g., a patch file, a markdown document) is committed.

LLMs are treated as untrusted "suggestion engines," not as trusted executors.

## Consequences

### Positive

-   **High Reliability**: The final output is guaranteed to be syntactically correct and compliant with all defined rules.
-   **Enhanced Safety**: Prevents hallucinations and other generative AI errors from impacting the user's data or performing irreversible actions.
-   **Auditability**: Each stage produces a verifiable artifact, creating a clear audit trail.
-   **Controlled Creativity**: Safely harnesses the power of LLMs for creative tasks without sacrificing determinism in execution.

### Negative

-   **Increased Latency**: The multi-stage pipeline is slower than a single end-to-end generative call.
-   **Implementation Complexity**: Requires building and maintaining a suite of deterministic validator tools for different domains (code, prose, etc.).
-   **Potential for Loops**: A poorly performing LLM might produce drafts that repeatedly fail validation, requiring sophisticated retry and feedback mechanisms.
