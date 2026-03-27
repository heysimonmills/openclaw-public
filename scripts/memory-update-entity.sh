#!/bin/bash
# Update entity with new atomic fact
# Usage: memory-update-entity.sh <entity-path> <fact> <category> [related-entities]

set -e

ENTITY_PATH=$1
FACT=$2
CATEGORY=$3
RELATED=${4:-""}

if [ -z "$ENTITY_PATH" ] || [ -z "$FACT" ] || [ -z "$CATEGORY" ]; then
    echo "Usage: memory-update-entity.sh <entity-path> <fact> <category> [related-entities]"
    echo "Example: memory-update-entity.sh life/areas/people/ian 'Loves sushi' preference"
    echo "Example: memory-update-entity.sh life/projects/good-jelly-co 'Launched new product' milestone 'life/areas/people/jacky'"
    echo ""
    echo "Categories: relationship, milestone, status, preference, context"
    exit 1
fi

ITEMS_FILE="/home/ubuntu/$ENTITY_PATH/items.json"

if [ ! -f "$ITEMS_FILE" ]; then
    echo "Error: Entity items.json not found at $ITEMS_FILE"
    exit 1
fi

# Generate unique ID
FACT_ID=$(echo "$FACT" | md5sum | cut -c1-8)
TODAY=$(date +%Y-%m-%d)

# Build related entities array
if [ -n "$RELATED" ]; then
    RELATED_JSON="[\"$RELATED\"]"
else
    RELATED_JSON="[]"
fi

# Add new fact to items.json
TMP_FILE=$(mktemp)
jq --arg id "$FACT_ID" \
   --arg fact "$FACT" \
   --arg category "$CATEGORY" \
   --arg timestamp "$TODAY" \
   --arg source "$TODAY" \
   --argjson related "$RELATED_JSON" \
   '.facts += [{
       "id": $id,
       "fact": $fact,
       "category": $category,
       "timestamp": $timestamp,
       "source": $source,
       "status": "active",
       "supersededBy": null,
       "relatedEntities": $related,
       "lastAccessed": $timestamp,
       "accessCount": 0
   }]' "$ITEMS_FILE" > "$TMP_FILE"

mv "$TMP_FILE" "$ITEMS_FILE"

echo "✓ Added fact to $ENTITY_PATH/items.json"
echo "  ID: $FACT_ID"
echo "  Fact: $FACT"
echo "  Category: $CATEGORY"

# Remind to update QMD index
echo ""
echo "Run 'qmd update' to re-index for search"
