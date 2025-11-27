#!/bin/bash

ADR_DIR="docs/architecture/design"
ADR_PATTERN="^adr-[0-9]{3}-([a-z0-9]+-)*[a-z0-9]+.md$"

EXIT_CODE=0

for FILE in $(find "$ADR_DIR" -type f -name "*.md"); do
  FILENAME=$(basename "$FILE")
  if [[ ! "$FILENAME" =~ $ADR_PATTERN ]]; then
    echo "ADR filename '$FILENAME' does not match the required format 'adr-XXX-kebab-case-description.md'"
    EXIT_CODE=1
  fi
done

exit $EXIT_CODE
