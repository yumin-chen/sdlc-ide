#!/bin/bash
set -e

OUTPUT_FILE="docs/events/SCHEMA_CATALOG.md"
SCHEMA_DIR="docs/events/schema-registry"
ENVELOPE_SCHEMA="$SCHEMA_DIR/common/EventEnvelope_v1.json"

# --- Header ---
{
    echo "# Event Schema Catalog"
    echo ""
    echo "This document provides a catalog of all event schemas, automatically generated from the JSON schema files."
    echo ""
} > "$OUTPUT_FILE"

# --- Function to render properties table ---
render_properties() {
    local schema_file=$1
    local properties_path=$2
    local required_path=$3

    {
        echo "| Property | Type | Description | Required |"
        echo "|---|---|---|---|"
    } >> "$OUTPUT_FILE"

    # Read all property keys into an array to avoid issues with pipes and subshells
    keys=($(jq -r "$properties_path | to_entries[] | .key" "$schema_file"))

    for key in "${keys[@]}"; do
        property_details=$(jq -r --arg key "$key" "$properties_path[\$key]" "$schema_file")

        type=$(echo "$property_details" | jq -r 'if .const then "const (`\(.const)`)" elif ."$ref" then "ref (`\(."$ref")`)" else .type end')
        description=$(echo "$property_details" | jq -r '.description')
        is_required=$(jq -r --arg key "$key" "if $required_path and ($required_path | index(\$key)) then \"Yes\" else \"No\" end" "$schema_file")
        enum_values=$(echo "$property_details" | jq -r '.enum | if . then " enum (`" + (.|join("`, `")) + "`)" else "" end')

        echo "| **\`$key\`** | \`$type$enum_values\` | $description | $is_required |" >> "$OUTPUT_FILE"
    done
}

# --- Render Envelope ---
{
    echo "## Common Envelope Properties (\`EventEnvelope.v1\`)"
    echo ""
    echo "All events share this common set of base properties."
    echo ""
} >> "$OUTPUT_FILE"
render_properties "$ENVELOPE_SCHEMA" ".properties" ".required"
echo "" >> "$OUTPUT_FILE"

# --- Render Event Schemas ---
for schema_file in $(find "$SCHEMA_DIR" -type f -name "*.json" ! -path "*/common/*"); do
    echo "Processing schema: $schema_file"

    title=$(jq -r '.title' "$schema_file")
    description=$(jq -r '.description' "$schema_file")

    {
        echo "---"
        echo "## $title"
        echo ""
        echo "**Description:** $description"
        echo ""
        echo "**Schema File:** [\`$(basename "$schema_file")\`](./schema-registry/$(basename "$schema_file"))"
        echo ""
        echo "### Event-Specific Properties"
        echo ""
    } >> "$OUTPUT_FILE"

    render_properties "$schema_file" ".allOf[1].properties" ".allOf[1].required"

    {
        echo ""
        echo "### Example"
        echo ""
        echo "\`\`\`json"
    } >> "$OUTPUT_FILE"

    jq '.examples[0]' "$schema_file" >> "$OUTPUT_FILE"

    {
        echo ""
        echo "\`\`\`"
        echo ""
    } >> "$OUTPUT_FILE"
done

echo "Schema catalog generated successfully at $OUTPUT_FILE"
