#!/usr/bin/env python3
"""
Get the Daily To-Dos database URL with info about creating a filtered view.
"""
import json

# Load config
with open('notion_config.json', 'r') as f:
    config = json.load(f)

db_id = config['tasks_db_id']
clean_id = db_id.replace('-', '')
db_url = f'https://www.notion.so/{clean_id}'

print(f"""
📋 Daily To-Dos Database
{db_url}

To create a filtered view for morning briefs:
1. Open the database in Notion
2. Click "+ New view" → Table view
3. Name it "Today & Overdue"
4. Add filters:
   - Due date → Is on or before → Today
   - Status → Does not equal → Done
5. Sort by: Due date (ascending)
6. Click "••" menu → Copy link to view

Then save that view link to use in morning briefs.
""")

print(f"\nDatabase URL: {db_url}")
