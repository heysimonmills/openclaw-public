# Goodreads Integration

Simon's Goodreads profile: https://www.goodreads.com/user/show/15854815-simon-mills
User ID: 15854815

## 2026 Reading Goal
**Target:** 12 books (1 per month)

## RSS Feeds
- All books: https://www.goodreads.com/review/list_rss/15854815
- Read shelf: https://www.goodreads.com/review/list_rss/15854815?shelf=read
- Currently reading: https://www.goodreads.com/review/list_rss/15854815?shelf=currently-reading
- To-read: https://www.goodreads.com/review/list_rss/15854815?shelf=to-read

## Scripts
- **Check progress:** `python3 .scripts/goodreads-2026-progress.py`
- **Quick view:** `.scripts/check-goodreads.sh`

## Integration with Goal Reviews
- **Monthly review (1st of month):** Pull books read in current year, check progress vs 1/month target
- **Quarterly review:** Check if on track (3 books/quarter)
- **Morning brief:** Currently reading book(s) shown occasionally

## Notes
- Goodreads API shut down in 2020, using RSS feeds instead
- Can read data, cannot write (Simon updates Goodreads manually)
- RSS updates whenever Simon logs a book
