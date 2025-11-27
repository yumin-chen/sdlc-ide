# Event Schema Registry

This folder contains the JSON schemas for the event types used in the SDLC_IDE system. These schemas are used to ensure consistency and compatibility across different versions of the events.

## Purpose

The schema registry is used to:
- Define the structure of events.
- Ensure compatibility between different versions of events.
- Provide documentation for event fields and their usage.

## Usage

1. **Adding New Schemas**: Add new JSON schema files to the `schema-registry` folder.
2. **Versioning**: Follow the versioning policy defined in `event-versioning-policy.md`.
3. **Validation**: Schemas are validated in CI using OPA/Conftest.
4. **Registration**: Use the provided scripts to register schemas with the Confluent Schema Registry.

## Schema Registration Workflow

1. Add the JSON schema to the repository.
2. Validate the schema in CI.
3. Register the schema with the Confluent Schema Registry.
4. Deploy producers/consumers after registry validation.

## Compatibility

Refer to the `compatibility-matrix.md` for details on compatibility modes and schema evolution status.
