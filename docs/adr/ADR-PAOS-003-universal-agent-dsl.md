# ADR-PAOS-003: Universal Agent DSL

- **Status**: Proposed
- **Date**: 2025-11-28
- **Deciders**: Yumin Chen

## Context and Problem Statement

To manage a diverse ecosystem of autonomous agents operating across different domains (programming, email, knowledge management), we need a standardized way to define tasks. Relying on unstructured natural language prompts alone is insufficient, as it leads to ambiguity, non-reproducibility, and makes it difficult to enforce constraints. An agent given a vague goal has too much freedom, increasing the risk of incorrect or undesirable outcomes.

We need a mechanism to define agent tasks in a way that is both expressive for the user and strictly machine-interpretable, ensuring that agent behavior is constrained, predictable, and repeatable.

## Decision Drivers

- **Reproducibility**: The same task definition should produce the same output every time (or within a narrow, predictable range for the generative step).
- **Constraint**: It must be possible to impose strict rules on an agent's allowed operations, scope, and output format.
- **Clarity**: The definition of a task should be unambiguous to both the user and the system.
- **Interoperability**: A universal format allows for easier orchestration and coordination between different types of agents.
- **Auditability**: A structured task definition provides a clear, auditable record of the agent's assigned goal and constraints.

## Considered Options

1.  **Natural Language with Prompt Engineering**: Rely on highly-structured natural language prompts and context, which is flexible but fails on reproducibility and strict constraint enforcement.
2.  **Proprietary Scripting Language**: Design a custom scripting language for defining agent workflows. This offers maximum power but comes with a steep learning curve and high implementation overhead.
3.  **Structured Data Format (DSL)**: Use a simple, declarative data format like YAML or JSON to define tasks. This provides a balance of structure, human-readability, and machine-interpretability.

## Decision Outcome

Chosen option: **"Structured Data Format (DSL)"**. All agent tasks in the PAOS will be defined using a universal, YAML-based Domain-Specific Language. This DSL will be the primary interface for initiating and controlling agent behavior.

The DSL will include, but is not limited to, the following key fields:
- `type`: The agent's domain (e.g., `programming`, `communication`, `knowledge_management`).
- `objective`: A natural language description of the goal.
- `target`: A precise specification of the resources the agent can operate on (e.g., file paths, email IDs, note titles).
- `operations`: An explicit list of allowed actions (e.g., `refactor`, `summarize`, `draft_reply`).
- `constraints`: Rules the agent must follow (e.g., `max_line_length: 80`, `tone: formal`, `output_format: json`).
- `context`: Instructions for fetching related information to inform the task.
- `output`: The desired format for the final artifact (e.g., `patch`, `markdown`, `email`).

This DSL serves as a "contract" that governs the agent's execution, providing clear boundaries for the generative "Draft" stage (ADR-PAOS-002).

## Consequences

### Positive

-   **Highly Predictable Behavior**: The DSL strictly limits the agent's scope and actions, leading to more reliable outcomes.
-   **Enhanced Security and Safety**: Prevents agents from accessing unauthorized files or performing destructive operations.
-   **Simplifies Orchestration**: A universal task format makes it easy for the orchestrator to manage and chain different agents together.
-   **Facilitates Templating**: Users can create and reuse templates for common tasks.

### Negative

-   **Reduced Flexibility**: The DSL is less flexible than pure natural language. Users must learn the specific schema and keywords.
-   **Schema Evolution**: The DSL schema will need to be versioned and maintained as new agent types and capabilities are added.
-   **Initial Overhead**: Requires upfront work to design and implement the DSL parser and validator.
