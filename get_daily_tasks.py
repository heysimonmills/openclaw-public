#!/usr/bin/env python3
"""
Get today's tasks + overdue tasks for morning brief.
Returns formatted text and database link.
"""
import json
import requests
from datetime import datetime, timezone

# Load config
with open('notion_config.json', 'r') as f:
    config = json.load(f)

API_KEY = config['api_key']
DATABASE_ID = config['tasks_db_id'].replace('-', '')

NOTION_API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_todays_and_overdue_tasks():
    """Query database for tasks due today or overdue."""
    url = f"{NOTION_API}/databases/{DATABASE_ID}/query"
    
    today = datetime.now(timezone.utc).date().isoformat()
    
    payload = {
        "filter": {
            "and": [
                {
                    "property": "Due date",
                    "date": {
                        "on_or_before": today
                    }
                },
                {
                    "property": "Status",
                    "status": {
                        "does_not_equal": "Done"
                    }
                }
            ]
        },
        "sorts": [
            {
                "property": "Due date",
                "direction": "ascending"
            },
            {
                "property": "Priority",
                "direction": "ascending"
            }
        ]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def format_task(task):
    """Format a single task."""
    properties = task['properties']
    
    # Extract task name
    title_prop = properties.get('Task name', {})
    title = ""
    if 'title' in title_prop:
        title_objects = title_prop.get('title', [])
        title = "".join([t.get('plain_text', '') for t in title_objects])
    
    # Extract category
    categories = []
    type_prop = properties.get('Task type', {})
    if 'multi_select' in type_prop:
        types = type_prop.get('multi_select', [])
        categories = [t.get('name', '') for t in types]
    
    # Extract priority
    priority = ""
    priority_prop = properties.get('Priority', {})
    if 'select' in priority_prop and priority_prop['select']:
        priority = priority_prop['select'].get('name', '')
    
    # Extract due date
    due_date = ""
    date_prop = properties.get('Due date', {})
    if 'date' in date_prop and date_prop['date']:
        due_date = date_prop['date'].get('start', '')
    
    # Build display
    parts = []
    if categories:
        parts.append(f"[{', '.join(categories)}]")
    parts.append(title)
    if priority:
        parts.append(f"({priority})")
    
    return " ".join(parts), due_date

if __name__ == "__main__":
    tasks = get_todays_and_overdue_tasks()
    today = datetime.now(timezone.utc).date()
    
    # Group by overdue vs today
    overdue = []
    today_tasks = []
    
    for task in tasks:
        formatted, due_date_str = format_task(task)
        if due_date_str:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
            if due_date < today:
                overdue.append((formatted, due_date))
            else:
                today_tasks.append((formatted, due_date))
    
    # Output
    print(f"📋 **Tasks for {today.strftime('%A, %B %d, %Y')}**\n")
    
    if overdue:
        print("⚠️ **Overdue:**")
        for task, due_date in overdue:
            days_ago = (today - due_date).days
            print(f"  • {task} (due {days_ago}d ago)")
        print()
    
    if today_tasks:
        print("📅 **Due Today:**")
        for task, _ in today_tasks:
            print(f"  • {task}")
        print()
    
    if not overdue and not today_tasks:
        print("✨ No tasks due today or overdue!\n")
    
    # Use filtered view URL if available, otherwise database URL
    view_url = config.get('tasks_today_view_url')
    if not view_url:
        view_url = f"https://www.notion.so/{config['tasks_db_id'].replace('-', '')}"
    print(f"📎 View in Notion: {view_url}")
