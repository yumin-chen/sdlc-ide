# Prompt: ADR Merger

## Context
You are a Senior Software Architect tasked with consolidating Architectural Decision Records (ADRs). You have two source files that address the same decision but from different perspectives:
1.  **Operational/Governance Perspective:** Often contains strict mandates, sovereignty requirements, specific tool selections (e.g., "Must use Podman for CI"), and compliance details.
2.  **Architectural/Design Perspective:** Often focuses on high-level patterns, standards (e.g., "OCI Compliance"), system integration (e.g., "systemd"), and theoretical security models (e.g., "Daemonless").

## Task
Merge these two documents into a single, authoritative ADR.

## Guidelines for Merging
1.  **Title:** Create a comprehensive title that reflects both the technology choice and the architectural standard (e.g., "Container Runtime & Technology Selection").
2.  **Decision:**
    *   Adopt the **stricter** decision. If one says "Recommended" and the other says "Mandatory," use **Mandatory**.
    *   Keep the **broader** standard. If one says "Podman" and the other says "OCI Containers," specify "Podman as the implementation of OCI Containers."
3.  **Rationale:**
    *   Combine distinct points. Do not lose the "Why".
    *   **Must Include:** Security architecture (daemonless, rootless), Standards compliance (OCI), and Governance/Sovereignty (no vendor lock-in, open source).
4.  **Alternatives:** List all unique alternatives from both files.
5.  **Consequences:**
    *   Include both **Positive** benefits (Security, Flexibility).
    *   Include **Negative** trade-offs (Compatibility issues, Learning curve).
    *   Include **Operational Mandates** (e.g., "CI must use X", "Developers must test on Y").

## Output Format
Use standard ADR Markdown format:
- Title & Status
- Context
- Decision
- Rationale (Numbered list)
- Alternatives Considered (Bulleted list)
- Consequences (Positive/Negative/Neutral)
- Related ADRs
