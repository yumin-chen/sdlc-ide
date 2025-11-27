# SDLC_IDE Integration with the Document SDK

This document outlines how the Document SDK will be integrated as a core, foundational component of the SDLC_IDE. The primary goal is to ensure that all documents generated or manipulated by the various agents within the SDLC_IDE are always in the canonical format, enforcing the rules defined in the `canonical-serializer-spec.md`.

## Core Principle: SDK as the Sole I/O Layer

No agent within the SDLC_IDE will be allowed to write directly to the filesystem. Instead, all document persistence operations (create, read, update, delete) MUST go through the Document SDK. The SDK will act as the single gateway to the Git working tree, ensuring that every document is validated and serialized correctly before being written.

## Integration Points

The integration will occur at several key points in the SDLC_IDE's workflow, mirroring the blueprint for a rich developer experience but applied to the autonomous agents.

| SDLC_IDE Integration Point             | SDK Component Used                  | Functionality Delivered                                                                                                                                                             |
| -------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Agent Document Generation**          | Document SDK (Serializer)           | When an agent like the `ADR_Manager` generates a new ADR, it will construct the document as an in-memory object. Before writing to disk, it will pass this object to the SDK's `serialize()` method. The SDK will handle the alphabetical sorting of keys, correct formatting, and writing the final YAML file. This guarantees that all machine-generated documents are born canonical. |
| **Agent Document Modification**        | Document SDK (Validator & Serializer) | If an agent needs to modify an existing document (e.g., changing the status of an ADR from "Proposed" to "Accepted"), it will first read the document using the SDK's `deserialize()` method. After modifying the in-memory object, it will use the `serialize()` method to write it back. This ensures that even partial updates result in a fully canonical file. |
| **Pre-Commit Validation (Internal)**   | Document SDK (Validator)            | Before an agent programmatically triggers a `git commit`, it will invoke the SDK's `validate()` method on all staged documents. This serves as a final check, mirroring the function of the pre-commit hook but within the automated workflow. If validation fails, the commit is aborted, and the error is logged. |
| **Commit Message Generation**          | Document SDK (Linter/Helper)        | The SDK will provide utilities for generating standardized commit messages based on the document's metadata. For example, when committing a new ADR, the SDK can help construct a message like `feat(docs): Add ADR-0012-new-feature-design`, ensuring consistency in the Git history. |

## Example Agent Workflow (ADR Manager)

1.  **Input:** The `ADR_Manager` receives a request to create a new ADR with specific content.
2.  **In-Memory Object:** The agent constructs an in-memory object representing the ADR. The keys are not necessarily sorted at this stage.
3.  **SDK Serialization:** The agent calls `DocumentSDK.save({ document: adrObject, path: 'docs/architecture/design/adr-0013-example.yaml' })`.
4.  **SDK Internal Steps:**
    a. The SDK takes the `adrObject`.
    b. It validates the object against the `adr_schema.json`. If invalid, it throws an error, which the agent must handle.
    c. It serializes the object to YAML, ensuring keys are sorted alphabetically, indentation is correct, and all other canonical rules are applied.
    d. It writes the resulting YAML string to the specified path.
5.  **Git Staging:** The `ADR_Manager` then uses `git add` to stage the newly created file.
6.  **Programmatic Commit:** Before committing, the agent calls `DocumentSDK.validateStaged()` as a final safeguard.
7.  **Commit:** The agent proceeds with `git commit`, using the SDK's helper to format the commit message.

By embedding the Document SDK this deeply into the agent lifecycle, the SDLC_IDE guarantees that it is a "good citizen" of the Git-native architecture, fully respecting the canonical format and providing the same level of integrity as the pre-commit hook and CI pipeline.
