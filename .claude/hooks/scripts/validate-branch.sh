#!/usr/bin/env bash
# Validates that the current Git branch follows the naming convention:
#   - main
#   - feature/{issue-number}-{description}

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)

if [ -z "$BRANCH" ]; then
    echo "Warning: not in a git repository, skipping branch validation."
    exit 0
fi

if [ "$BRANCH" = "main" ]; then
    exit 0
fi

if [[ "$BRANCH" =~ ^feature/[0-9]+-[a-z0-9][a-z0-9-]*$ ]]; then
    exit 0
fi

echo "ERROR: Branch name '$BRANCH' does not follow the naming convention."
echo "Allowed patterns:"
echo "  - main"
echo "  - feature/{issue-number}-{description}  (e.g., feature/12-add-demographic-parity)"
exit 1
