#!/usr/bin/env python3
"""
Check Goodreads progress toward 2026 goal (12 books)
User: Simon Mills (15854815)
"""

import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

USER_ID = "15854815"
GOAL_BOOKS = 12
YEAR = 2026

def get_books_read_in_year(user_id, year):
    """Fetch books read in specified year from Goodreads RSS feed."""
    url = f"https://www.goodreads.com/review/list_rss/{user_id}?shelf=read"
    
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        books = []
        
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            read_at_elem = item.find('user_read_at')
            rating_elem = item.find('user_rating')
            
            if title_elem is not None and read_at_elem is not None:
                title = title_elem.text
                read_at = read_at_elem.text
                rating = rating_elem.text if rating_elem is not None else "0"
                
                # Check if read in target year
                if read_at and str(year) in read_at:
                    books.append({
                        'title': title,
                        'read_at': read_at,
                        'rating': rating
                    })
        
        return books
    
    except Exception as e:
        print(f"Error fetching Goodreads data: {e}")
        return []

def main():
    books = get_books_read_in_year(USER_ID, YEAR)
    count = len(books)
    
    print(f"📚 2026 Reading Goal Progress")
    print(f"{'='*40}")
    print(f"Books read: {count}/{GOAL_BOOKS}")
    print(f"Progress: {(count/GOAL_BOOKS)*100:.1f}%")
    print(f"On track: {'✓ Yes' if count >= (datetime.now().month) else '⚠️ Behind'}")
    print(f"")
    
    if books:
        print(f"Books read in {YEAR}:")
        for i, book in enumerate(books, 1):
            stars = "⭐" * int(book['rating']) if book['rating'] != "0" else "No rating"
            print(f"{i}. {book['title']} - {stars}")
    else:
        print(f"No books finished yet in {YEAR}")
    
    print(f"")
    print(f"Target: 1 book per month = 12 books by Dec 31")
    remaining = GOAL_BOOKS - count
    if remaining > 0:
        print(f"Remaining: {remaining} books")
    else:
        print(f"🎉 Goal achieved!")

if __name__ == "__main__":
    main()
