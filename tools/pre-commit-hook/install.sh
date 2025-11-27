#!/bin/sh

# This script installs the pre-commit hook into the local .git/hooks directory.
# It should be triggered on SDK setup (e.g., via 'npm postinstall').

if [ -d ".git" ]; then
    HOOK_DIR=".git/hooks"
    PRE_COMMIT_HOOK="$HOOK_DIR/pre-commit"

    echo "Installing Document SDK pre-commit hook..."

    # Create the hooks directory if it doesn't exist
    mkdir -p "$HOOK_DIR"

    # Copy the hook script
    cp "$(dirname "$0")/pre-commit" "$PRE_COMMIT_HOOK"

    # Make it executable
    chmod +x "$PRE_COMMIT_HOOK"

    echo "Pre-commit hook installed successfully."
else
    echo "Not inside a Git repository. Skipping pre-commit hook installation."
fi
