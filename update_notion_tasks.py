#!/usr/bin/env python3
import json
import requests
import os
import sys
from datetime import datetime, timedelta

# Load Notion API key
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

def create_task(task_name, category, due_date=None, priority=None, description=None):
    """Create a new task in Notion with the given details."""
    url = f"{NOTION_API}/pages"
    
    # Handle category (Task type in the database)
    category_names = {
        "GSG": "💼 GSG", 
        "GJC": "🍯 GJC",
        "PERSONAL": "🏠 Personal"
    }
    category_name = category_names.get(category.upper(), "🏠 Personal")
    
    # Parse relative date
    if due_date:
        today = datetime.now()
        if due_date.lower() == "today" or due_date.lower() == "tonight":
            date_string = today.strftime("%Y-%m-%d")
        elif due_date.lower() == "tomorrow":
            date_string = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "next week" in due_date.lower():
            date_string = (today + timedelta(days=7)).strftime("%Y-%m-%d")
        else:
            date_string = due_date
    else:
        date_string = None
    
    # Build properties
    properties = {
        "Task name": {
            "title": [
                {
                    "text": {
                        "content": task_name
                    }
                }
            ]
        },
        "Status": {
            "status": {
                "name": "Not started"
            }
        }
    }
    
    # Add Task type (category)
    properties["Task type"] = {
        "multi_select": [
            {
                "name": category_name
            }
        ]
    }
    
    # Add due date if provided
    if date_string:
        properties["Due date"] = {
            "date": {
                "start": date_string
            }
        }
    
    # Add priority if provided
    if priority:
        properties["Priority"] = {
            "select": {
                "name": priority
            }
        }
    
    # Create the request payload
    payload = {
        "parent": {
            "database_id": DATABASE_ID
        },
        "properties": properties
    }
    
    # Add description if provided
    if description:
        payload["children"] = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": description
                            }
                        }
                    ]
                }
            }
        ]
    
    # Make the API request
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        return {"success": True, "task_id": response.json().get("id"), "task_name": task_name}
    else:
        print(f"Error creating task: {response.status_code}")
        print(response.text)
        return {"success": False, "error": response.text}

# Tasks to add
tasks = [
    {"name": "do the GJC tiktok slideshow", "category": "GJC", "due_date": "tomorrow"},
    {"name": "setup GJC on Faire", "category": "GJC", "due_date": "tomorrow"},
    {"name": "make the intro video", "category": "GJC", "due_date": "tomorrow"},
    {"name": "do laundry and dish", "category": "personal", "due_date": "today"},
    {"name": "welcome emails", "category": "GJC", "due_date": "tomorrow"}
]

# Add all tasks and collect results
results = []
for task in tasks:
    result = create_task(
        task_name=task["name"],
        category=task["category"],
        due_date=task.get("due_date"),
        priority=task.get("priority"),
        description=task.get("description")
    )
    results.append(result)

# Print summary of results
for result in results:
    if result["success"]:
        print(f"✅ Added task: {result['task_name']}")
    else:
        print(f"❌ Failed to add task: {result.get('task_name', 'Unknown')}")