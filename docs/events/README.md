# Event Schema Registry

This folder contains the JSON schemas for the event types used in the SDLC_IDE system. These schemas are used to ensure consistency and compatibility across different versions of the events.

## Schema Catalog

A full catalog of all event schemas, including descriptions and examples, is available in the [**Schema Catalog**](./SCHEMA_CATALOG.md).

## Style Guide

All schemas must adhere to the conventions defined in the [Event Schema Style Guide](./event-style-guide.md).

## Usage

1. **Adding New Schemas**: Add new JSON schema files to the `schema-registry` folder.
2. **Versioning**: Follow the versioning policy defined in `event-versioning-policy.md`.
3. **Validation**: Schemas are validated in CI using `ajv-cli`.
4. **Registration**: Use the provided scripts to register schemas with the Confluent Schema Registry.

## Schema Registration Workflow

1. Add the JSON schema to the repository.
2. Validate the schema in CI.
3. Register the schema with the Confluent Schema Registry.
4. Deploy producers/consumers after registry validation.

## Compatibility

Refer to the `compatibility-matrix.md` for details on compatibility modes and schema evolution status.
