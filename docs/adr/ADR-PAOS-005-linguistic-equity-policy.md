# ADR-PAOS-005: Linguistic Equity Policy for Documentation

- **Status**: Accepted
- **Date**: 2025-11-28
- **Deciders**: Yumin Chen

## Context
Most open-source projects default to English for documentation.
While practical, this default reinforces linguistic dominance and excludes non-English speakers.

The goal of this repository is to:
- be globally accessible
- avoid privileging any language
- challenge default linguistic hierarchies
- maintain practical usability for developers worldwide

## Decision
1. The repository SHALL NOT designate any single “default” documentation language.
2. The top-level README SHALL contain:
   - no descriptive text in any natural language
   - only a neutral symbolic header (“🌍”)
   - a list of languages written in their *native endonyms*
   - links to individual README files for each language
3. The ordering of languages SHALL follow alphabetical sorting by native endonym.
4. Each language SHALL have its own `README.<code>.md`.
5. A generation script maintains consistency and prevents manual bias.

## Consequences
- No language is privileged structurally.
- Global contributors find documentation in their own language.
- English remains supported, but not elevated.
- Fully automated index prevents accidental prioritization.

## Notes
This ADR establishes a long-term foundation for culturally neutral, inclusive documentation.
