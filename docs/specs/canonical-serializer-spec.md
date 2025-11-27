# Canonical Serializer Specification

This document defines the non-negotiable format for all documents stored within the Git repository, ensuring determinism, neutrality, and readability. All documents, whether created by a human or a machine, MUST adhere to this specification.

The Document SDK and the CI validation pipeline are the primary enforcers of this specification.

## Core Requirements

| Requirement             | Description                                                                                             | Rationale                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Format**              | YAML (as a strict subset of JSON)                                                                       | Human-readable, supports comments, and natively handles structured data.         |
| **Field Ordering**      | Strict Alphabetical Key Ordering                                                                        | Critical for generating deterministic diffs, preventing noise in commits.        |
| **Indentation**         | 2 spaces, no tabs.                                                                                      | A universal standard for YAML/JSON consistency.                                  |
| **Line Endings**        | LF only (`\n`).                                                                                         | Prevents platform-specific diff noise (CRLF vs. LF).                             |
| **Neutrality**          | No Vendor/Tooling Metadata                                                                              | The serializer MUST strip proprietary or tool-specific fields (e.g., `_last_edited_by`). |
| **String Quoting**      | Minimal Quoting                                                                                         | Prefer plain scalars. Only quote strings when necessary (e.g., contains special characters). |
| **Standard Structure**  | Required Top-Level Fields                                                                               | Each document type MUST conform to its registered JSON Schema (see `/schemas`).  |
