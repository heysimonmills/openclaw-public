#!/usr/bin/env python3
"""
Update a Notion page with today's tasks + overdue tasks.
Creates a clean, readable page that gets updated daily.
"""
import json
import requests
import os
from datetime import datetime, timezone, timedelta

# Load config
config_path = os.path.join(os.path.dirname(__file__), 'notion_config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

API_KEY = config['api_key']
DATABASE_ID = config['tasks_db_id'].replace('-', '')

# API Constants
NOTION_API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# Page ID for the Daily To-Dos page (will be created if doesn't exist)
DAILY_TODOS_PAGE_ID = config.get('daily_todos_page_id')

def get_todays_and_overdue_tasks():
    """Query database for tasks due today or overdue."""
    url = f"{NOTION_API}/databases/{DATABASE_ID}/query"
    
    today = datetime.now(timezone.utc).date().isoformat()
    
    # Get tasks due today or before (overdue)
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
            }
        ]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Error querying tasks: {response.status_code}")
        print(response.text)
        return []

def create_daily_todos_page():
    """Create the Daily To-Dos page."""
    url = f"{NOTION_API}/pages"
    
    payload = {
        "parent": {
            "type": "database_id",
            "database_id": DATABASE_ID  # Create as a page in the tasks database
        },
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": "📋 Today's To-Dos"
                        }
                    }
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Loading tasks..."}
                        }
                    ]
                }
            }
        ]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        page_data = response.json()
        page_id = page_data['id']
        
        # Save page ID to config
        config['daily_todos_page_id'] = page_id
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return page_id
    else:
        print(f"Error creating page: {response.status_code}")
        print(response.text)
        return None

def clear_page_content(page_id):
    """Delete all blocks from a page."""
    # Get all blocks
    url = f"{NOTION_API}/blocks/{page_id}/children"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        blocks = response.json().get('results', [])
        
        # Delete each block
        for block in blocks:
            delete_url = f"{NOTION_API}/blocks/{block['id']}"
            requests.delete(delete_url, headers=HEADERS)

def update_page_content(page_id, tasks):
    """Update the page with current tasks."""
    # Clear existing content
    clear_page_content(page_id)
    
    # Build new content
    today = datetime.now(timezone.utc).date()
    
    children = [
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": f"📋 Tasks for {today.strftime('%A, %B %d, %Y')}"}
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": f"Last updated: {datetime.now(timezone.utc).strftime('%I:%M %p')} UTC"}
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "divider",
            "divider": {}
        }
    ]
    
    if not tasks:
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "✨ No tasks due today or overdue!"}
                    }
                ]
            }
        })
    else:
        # Group by overdue vs today
        overdue_tasks = []
        today_tasks = []
        
        for task in tasks:
            due_date_prop = task['properties'].get('Due date', {})
            if 'date' in due_date_prop and due_date_prop['date']:
                due_date_str = due_date_prop['date'].get('start', '')
                if due_date_str:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
                    if due_date < today:
                        overdue_tasks.append(task)
                    else:
                        today_tasks.append(task)
        
        # Add overdue section
        if overdue_tasks:
            children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "⚠️ Overdue"}
                        }
                    ]
                }
            })
            
            for task in overdue_tasks:
                children.append(create_task_block(task))
        
        # Add today section
        if today_tasks:
            children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "📅 Due Today"}
                        }
                    ]
                }
            })
            
            for task in today_tasks:
                children.append(create_task_block(task))
    
    # Update page with new blocks
    url = f"{NOTION_API}/blocks/{page_id}/children"
    
    # Notion API limits to 100 blocks per request
    for i in range(0, len(children), 100):
        batch = children[i:i+100]
        payload = {"children": batch}
        response = requests.patch(url, headers=HEADERS, json=payload)
        
        if response.status_code != 200:
            print(f"Error updating page: {response.status_code}")
            print(response.text)

def create_task_block(task):
    """Create a formatted block for a task."""
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
    
    # Extract status
    status = ""
    status_prop = properties.get('Status', {})
    if 'status' in status_prop and status_prop['status']:
        status = status_prop['status'].get('name', '')
    
    # Extract priority
    priority = ""
    priority_prop = properties.get('Priority', {})
    if 'select' in priority_prop and priority_prop['select']:
        priority = priority_prop['select'].get('name', '')
    
    # Build display text
    display_text = title
    if categories:
        display_text += f" ({', '.join(categories)})"
    if priority:
        display_text += f" • {priority}"
    if status:
        display_text += f" • {status}"
    
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": display_text}
                }
            ],
            "checked": False
        }
    }

def get_page_url(page_id):
    """Get the shareable URL for a page."""
    # Format: https://notion.so/{page_id}
    return f"https://notion.so/{page_id.replace('-', '')}"

if __name__ == "__main__":
    # Get or create the Daily To-Dos page
    if not DAILY_TODOS_PAGE_ID:
        print("Creating Daily To-Dos page...")
        DAILY_TODOS_PAGE_ID = create_daily_todos_page()
        if not DAILY_TODOS_PAGE_ID:
            print("Failed to create page")
            exit(1)
    
    # Get today's and overdue tasks
    print("Fetching tasks...")
    tasks = get_todays_and_overdue_tasks()
    print(f"Found {len(tasks)} tasks")
    
    # Update the page
    print("Updating page...")
    update_page_content(DAILY_TODOS_PAGE_ID, tasks)
    
    # Output the page URL
    page_url = get_page_url(DAILY_TODOS_PAGE_ID)
    print(f"\n✓ Daily To-Dos page updated: {page_url}")
