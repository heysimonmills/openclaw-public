#!/bin/bash
# search-knowledge.sh - Helper script for searching across PARA and memory using QMD

usage() {
    echo "Usage: $0 [OPTIONS] <query>"
    echo ""
    echo "Options:"
    echo "  -c, --collection <name>   Search specific collection (life|memory|clawd)"
    echo "  -l, --limit <n>           Limit results (default: 5)"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 'Ian boyfriend'                    # Search all collections"
    echo "  $0 -c life 'water polo friends'       # Search only PARA structure"
    echo "  $0 -c memory 'calendar events'        # Search only daily notes"
    echo "  $0 -l 10 'George St Growth clients'   # Get more results"
    exit 1
}

# Default values
COLLECTION=""
LIMIT=5
QUERY=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--collection)
            COLLECTION="$2"
            shift 2
            ;;
        -l|--limit)
            LIMIT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            QUERY="$QUERY $1"
            shift
            ;;
    esac
done

# Trim leading/trailing whitespace
QUERY=$(echo "$QUERY" | xargs)

if [ -z "$QUERY" ]; then
    echo "Error: Query is required"
    usage
fi

# Build QMD command
CMD="qmd search \"$QUERY\""

if [ -n "$COLLECTION" ]; then
    CMD="$CMD -c $COLLECTION"
fi

CMD="$CMD -n $LIMIT"

# Execute search
echo "Searching for: $QUERY"
if [ -n "$COLLECTION" ]; then
    echo "Collection: $COLLECTION"
fi
echo "---"
eval $CMD
