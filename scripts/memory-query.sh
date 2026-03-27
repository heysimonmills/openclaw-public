#!/bin/bash
# Semantic search across all memory collections
# Usage: memory-query.sh <query> [collection]

set -e

QUERY=$1
COLLECTION=${2:-""}

# Add bun to PATH
export PATH="$HOME/.bun/bin:$PATH"

if [ -z "$QUERY" ]; then
    echo "Usage: memory-query.sh <query> [collection]"
    echo "Example: memory-query.sh 'Simon water polo schedule'"
    echo "Example: memory-query.sh 'Ian preferences' life"
    echo ""
    echo "Collections: life, memory, clawd"
    exit 1
fi

if [ -n "$COLLECTION" ]; then
    echo "=== Searching in '$COLLECTION' collection ==="
    qmd search "$QUERY" -c "$COLLECTION" -n 10
else
    echo "=== Searching across all collections ==="
    qmd search "$QUERY" -n 10
fi
