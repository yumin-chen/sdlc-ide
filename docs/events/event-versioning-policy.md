# Event Versioning Policy

## 1. Semantic Event Versioning

Events follow the rule:

`<event_name>.v<major>`

- **Major Versions**: Incremented for breaking changes.
- **Minor Versions**: Do not exist. All non-breaking changes stay within the same major version.

## 2. Compatibility Rules

Set schema registry rule:

**BACKWARD compatibility** (recommended)

Supports downstream consumers that lag behind producers.

## 3. Breaking vs. Non-Breaking Changes

### Breaking Changes (Bump to v2)
- Remove a field
- Change type (string → int)
- Rename fields
- Make optional → required
- Change semantic meaning
- Remove enum member

### Non-Breaking Changes (Stay in v1)
- Add new optional fields
- Add new enum members
- Add metadata fields
- Add foreign-key references
- Deprecate fields

## 4. Schema Registration Workflow

1. **Add JSON schema to repository**: Store schema definitions in `/docs/events/schema-registry/`.
2. **OPA / Conftest validation**: Validate schemas in CI.
3. **Register schema**: Use scripts to register schemas with the Confluent Schema Registry.
4. **Deploy producers/consumers**: Deploy only after registry validation.
