#!/bin/bash
# Tiered memory search: Summary → QMD → Full facts
# Usage: memory-search.sh <entity-name> [query]

set -e

ENTITY=$1
QUERY=${2:-""}
LIFE_DIR="/home/ubuntu/life"

# Add bun to PATH
export PATH="$HOME/.bun/bin:$PATH"

if [ -z "$ENTITY" ]; then
    echo "Usage: memory-search.sh <entity-name> [query]"
    echo "Example: memory-search.sh ian"
    echo "Example: memory-search.sh simon 'schedule preferences'"
    exit 1
fi

# Tier 1: Check for entity summary (fastest)
SUMMARY_PATHS=(
    "$LIFE_DIR/areas/people/$ENTITY/summary.md"
    "$LIFE_DIR/areas/companies/$ENTITY/summary.md"
    "$LIFE_DIR/projects/$ENTITY/summary.md"
)

for SUMMARY in "${SUMMARY_PATHS[@]}"; do
    if [ -f "$SUMMARY" ]; then
        echo "=== TIER 1: Entity Summary ==="
        cat "$SUMMARY"
        echo ""
        
        # If no specific query, stop here
        if [ -z "$QUERY" ]; then
            exit 0
        fi
        break
    fi
done

# Tier 2: QMD semantic search (if query provided)
if [ -n "$QUERY" ]; then
    echo "=== TIER 2: QMD Search Results ==="
    qmd search "$QUERY" -c life -n 5 2>/dev/null || echo "QMD search failed"
    echo ""
fi

# Tier 3: Full facts from items.json (if exists)
ITEMS_PATHS=(
    "$LIFE_DIR/areas/people/$ENTITY/items.json"
    "$LIFE_DIR/areas/companies/$ENTITY/items.json"
    "$LIFE_DIR/projects/$ENTITY/items.json"
)

for ITEMS in "${ITEMS_PATHS[@]}"; do
    if [ -f "$ITEMS" ]; then
        echo "=== TIER 3: Full Atomic Facts ==="
        if [ -n "$QUERY" ]; then
            # Filter facts by query keywords
            jq --arg query "$QUERY" '.facts[] | select(.status == "active") | select(.fact | ascii_downcase | contains($query | ascii_downcase))' "$ITEMS" 2>/dev/null || cat "$ITEMS"
        else
            # Show all active facts
            jq '.facts[] | select(.status == "active")' "$ITEMS" 2>/dev/null || cat "$ITEMS"
        fi
        exit 0
    fi
done

echo "Entity '$ENTITY' not found in PARA structure"
exit 1
