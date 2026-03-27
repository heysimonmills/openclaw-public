#!/usr/bin/env python3
"""
Create and update a standalone Notion page with today's tasks.
This page is shareable and easy to read.
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
            }
        ]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def create_page():
    """Create the daily tasks page in workspace."""
    url = f"{NOTION_API}/pages"
    
    today = datetime.now(timezone.utc).date()
    
    payload = {
        "parent": {
            "type": "page_id",
            "page_id": "2f644b5eebe58008ba14fd08cbb1a341"  # Try this workspace ID
        },
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": "📋 Today's Tasks"
                        }
                    }
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"Tasks for {today.strftime('%A, %B %d, %Y')}"}
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
        page_url = page_data['url']
        
        # Save to config
        config['daily_tasks_page_id'] = page_id
        config['daily_tasks_page_url'] = page_url
        with open('notion_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        return page_id, page_url
    else:
        print(f"Error creating page: {response.status_code}")
        print(response.text)
        return None, None

def clear_page_blocks(page_id):
    """Clear all blocks from a page."""
    url = f"{NOTION_API}/blocks/{page_id}/children"
    params = {"page_size": 100}
    
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        blocks = response.json().get('results', [])
        for block in blocks:
            delete_url = f"{NOTION_API}/blocks/{block['id']}"
            requests.delete(delete_url, headers=HEADERS)

def update_page(page_id, tasks):
    """Update page with current tasks."""
    clear_page_blocks(page_id)
    
    today = datetime.now(timezone.utc).date()
    
    # Build content blocks
    blocks = [
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
                        "text": {"content": f"Updated: {datetime.now(timezone.utc).strftime('%I:%M %p UTC')}"}
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
        blocks.append({
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
        # Group tasks
        overdue = []
        today_tasks = []
        
        for task in tasks:
            due_date_prop = task['properties'].get('Due date', {})
            if 'date' in due_date_prop and due_date_prop['date']:
                due_date_str = due_date_prop['date'].get('start', '')
                if due_date_str:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
                    if due_date < today:
                        overdue.append(task)
                    else:
                        today_tasks.append(task)
        
        # Add overdue section
        if overdue:
            blocks.append({
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
            
            for task in overdue:
                blocks.append(format_task_block(task, today))
        
        # Add today section
        if today_tasks:
            blocks.append({
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
                blocks.append(format_task_block(task, today))
    
    # Add blocks in batches of 100
    url = f"{NOTION_API}/blocks/{page_id}/children"
    for i in range(0, len(blocks), 100):
        batch = blocks[i:i+100]
        payload = {"children": batch}
        response = requests.patch(url, headers=HEADERS, json=payload)
        if response.status_code != 200:
            print(f"Error updating page: {response.status_code}")
            print(response.text)

def format_task_block(task, today):
    """Format a task as a to-do block."""
    properties = task['properties']
    
    # Extract details
    title_prop = properties.get('Task name', {})
    title = ""
    if 'title' in title_prop:
        title_objects = title_prop.get('title', [])
        title = "".join([t.get('plain_text', '') for t in title_objects])
    
    categories = []
    type_prop = properties.get('Task type', {})
    if 'multi_select' in type_prop:
        types = type_prop.get('multi_select', [])
        categories = [t.get('name', '') for t in types]
    
    priority = ""
    priority_prop = properties.get('Priority', {})
    if 'select' in priority_prop and priority_prop['select']:
        priority = priority_prop['select'].get('name', '')
    
    due_date_prop = properties.get('Due date', {})
    due_info = ""
    if 'date' in due_date_prop and due_date_prop['date']:
        due_date_str = due_date_prop['date'].get('start', '')
        if due_date_str:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
            if due_date < today:
                days_ago = (today - due_date).days
                due_info = f" • {days_ago}d overdue"
    
    # Build text
    text = title
    if categories:
        text = f"[{', '.join(categories)}] {text}"
    if priority:
        text += f" ({priority})"
    if due_info:
        text += due_info
    
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ],
            "checked": False
        }
    }

if __name__ == "__main__":
    import sys
    
    # Check if page exists
    page_id = config.get('daily_tasks_page_id')
    page_url = config.get('daily_tasks_page_url')
    
    if not page_id:
        print("Creating new daily tasks page...")
        page_id, page_url = create_page()
        if not page_id:
            print("Failed to create page. Trying without parent...")
            # Try creating without parent
            url = f"{NOTION_API}/pages"
            today = datetime.now(timezone.utc).date()
            
            payload = {
                "parent": {
                    "type": "workspace",
                    "workspace": True
                },
                "properties": {
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": "📋 Today's Tasks"
                                }
                            }
                        ]
                    }
                }
            }
            
            response = requests.post(url, headers=HEADERS, json=payload)
            if response.status_code == 200:
                page_data = response.json()
                page_id = page_data['id']
                page_url = page_data['url']
                
                config['daily_tasks_page_id'] = page_id
                config['daily_tasks_page_url'] = page_url
                with open('notion_config.json', 'w') as f:
                    json.dump(config, f, indent=2)
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
                sys.exit(1)
    
    print(f"Page ID: {page_id}")
    print(f"Page URL: {page_url}")
    
    # Get tasks
    print("\nFetching tasks...")
    tasks = get_todays_and_overdue_tasks()
    print(f"Found {len(tasks)} tasks")
    
    # Update page
    print("Updating page...")
    update_page(page_id, tasks)
    
    print(f"\n✓ Page updated: {page_url}")
