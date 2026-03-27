#!/bin/bash
# Check Goodreads reading progress for Simon Mills
# User ID: 15854815

USER_ID="15854815"
YEAR=$(date +%Y)

echo "📚 Goodreads Reading Progress for $YEAR"
echo "========================================"
echo ""

# Get read books (recent)
echo "Recently finished books:"
curl -s "https://www.goodreads.com/review/list_rss/$USER_ID?shelf=read" | \
  grep -E "<user_read_at>|<title>" | \
  grep -A 1 "user_read_at" | \
  grep -B 1 "$YEAR" | \
  sed 's/<[^>]*>//g' | \
  sed 's/^\s*//' | \
  paste -d " - " - - | \
  head -20

echo ""
echo "Currently reading:"
curl -s "https://www.goodreads.com/review/list_rss/$USER_ID?shelf=currently-reading" | \
  grep "<title>" | \
  sed 's/<[^>]*>//g' | \
  sed 's/^\s*//' | \
  grep -v "bookshelf" | \
  head -10

echo ""
echo "To-read list (first 5):"
curl -s "https://www.goodreads.com/review/list_rss/$USER_ID?shelf=to-read" | \
  grep "<title>" | \
  sed 's/<[^>]*>//g' | \
  sed 's/^\s*//' | \
  grep -v "bookshelf" | \
  head -5
