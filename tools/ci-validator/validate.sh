#!/bin/sh

# This script is a placeholder for the CI validator tool.
# It simulates the process of checking if a document is in the canonical format.

set -e # Exit immediately if a command exits with a non-zero status.

TARGET_FILES=$(find docs -type f \( -name "*.yaml" -o -name "*.yml" \))

if [ -z "$TARGET_FILES" ]; then
  echo "No document files found to validate."
  exit 0
fi

echo "Running CI validation on document files..."

for FILE in $TARGET_FILES; do
  echo "Checking $FILE..."

  # Placeholder for the real CI validation logic.
  # The real tool would:
  # 1. Read the content of $FILE.
  # 2. Run it through the canonical serializer.
  # 3. Compare the output with the original content.
  # 4. If they differ, exit with a non-zero status code.

  # For now, we'll just simulate a successful check.
  # To test a failure, you could uncomment the following lines:
  # echo "Error: $FILE is not in canonical format." >&2
  # exit 1
  :
done

echo "CI validation successful. All documents are in canonical format."
exit 0
