#!/bin/bash
#
# Git Pre-receive Hook
# Rejects pushes that violate OPA policies.
#
# Usage: Copy to .git/hooks/pre-receive (on server) or use with a tool like husky for local pre-push (adapted).
#

OPA_URL="http://localhost:8181/v1/data/sdlc/governance/allow"
ZERO_COMMIT="0000000000000000000000000000000000000000"

while read oldrev newrev refname; do
    # 1. Identify the user and branch
    USER=$(whoami)
    BRANCH=${refname#refs/heads/}

    # 2. Get list of changed files
    if [ "$oldrev" = "$ZERO_COMMIT" ]; then
        # New branch
        CHANGED_FILES=$(git ls-tree -r --name-only $newrev)
    else
        CHANGED_FILES=$(git diff --name-only $oldrev $newrev)
    fi

    # Convert newline separated files to JSON array
    FILES_JSON=$(echo "$CHANGED_FILES" | jq -R . | jq -s .)

    # 3. Construct OPA Input
    # Note: In a real hook, you'd extract more metadata (e.g. is this a merge commit?)
    INPUT_JSON=$(jq -n \
                  --arg user "$USER" \
                  --arg branch "$BRANCH" \
                  --argjson files "$FILES_JSON" \
                  '{
                    event_type: "push",
                    actor: $user,
                    branch: $branch,
                    changed_files: $files
                  }')

    # 4. Query OPA
    RESPONSE=$(curl -s -X POST "$OPA_URL" -H "Content-Type: application/json" -d "{\"input\": $INPUT_JSON}")
    ALLOWED=$(echo "$RESPONSE" | jq -r '.result')

    # 5. Enforce
    if [ "$ALLOWED" != "true" ]; then
        echo "----------------------------------------------------"
        echo "🚫 PUSH REJECTED BY GOVERNANCE POLICY"
        echo "   You are attempting to modify protected files."
        echo "   ADR changes must be made via Pull Request."
        echo "----------------------------------------------------"
        exit 1
    fi
done

exit 0
