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

def get_todays_tasks():
    """Get all tasks due today that aren't completed"""
    url = f"{NOTION_API}/databases/{DATABASE_ID}/query"
    
    # Get today's date in ISO format
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Query for tasks due today that aren't done
    payload = {
        "filter": {
            "and": [
                {
                    "property": "Due date",
                    "date": {
                        "equals": today
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
                "property": "Task name",
                "direction": "ascending"
            }
        ]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Error getting today's tasks: {response.status_code}")
        print(response.text)
        return []

def get_next_business_day():
    """Get the next business day (skip weekends)"""
    today = datetime.now()
    next_day = today + timedelta(days=1)
    
    # If next day is Saturday, skip to Monday
    if next_day.weekday() == 5:  # Saturday
        next_day = today + timedelta(days=3)
    # If next day is Sunday, skip to Monday
    elif next_day.weekday() == 6:  # Sunday
        next_day = today + timedelta(days=2)
    
    return next_day.strftime("%Y-%m-%d")

def update_task_due_date(task_id, new_date):
    """Update the due date of a task"""
    url = f"{NOTION_API}/pages/{task_id}"
    
    payload = {
        "properties": {
            "Due date": {
                "date": {
                    "start": new_date
                }
            }
        }
    }
    
    response = requests.patch(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        return True
    else:
        print(f"Error updating task due date: {response.status_code}")
        print(response.text)
        return False

def update_task_status(task_id, status):
    """Update the status of a task"""
    url = f"{NOTION_API}/pages/{task_id}"
    
    payload = {
        "properties": {
            "Status": {
                "status": {
                    "name": status
                }
            }
        }
    }
    
    response = requests.patch(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        return True
    else:
        print(f"Error updating task status: {response.status_code}")
        print(response.text)
        return False

def extract_task_details(task):
    """Extract readable details from a task object"""
    properties = task.get("properties", {})
    
    # Extract title
    title_prop = properties.get("Task name", {})
    title = ""
    if "title" in title_prop:
        title_objects = title_prop.get("title", [])
        title = "".join([t.get("plain_text", "") for t in title_objects])
    
    # Extract status
    status_prop = properties.get("Status", {})
    status = ""
    if "status" in status_prop and status_prop["status"]:
        status = status_prop["status"].get("name", "Unknown")
    
    # Extract task type (category)
    type_prop = properties.get("Task type", {})
    category = []
    if "multi_select" in type_prop:
        types = type_prop.get("multi_select", [])
        category = [t.get("name", "") for t in types]
    
    return {
        "id": task.get("id"),
        "name": title,
        "status": status,
        "category": category
    }

def format_task_summary(tasks):
    """Format a list of tasks into a readable message"""
    if not tasks:
        return "No tasks due today! 🎉"
    
    output = []
    for task in tasks:
        details = extract_task_details(task)
        category_tag = ""
        if details.get("category"):
            # Get first category
            cat = details.get("category")[0] if details.get("category") else ""
            if "GSG" in cat:
                category_tag = "💼 GSG"
            elif "GJC" in cat:
                category_tag = "🍯 GJC"
            elif "Personal" in cat:
                category_tag = "🏠 Personal"
        
        task_line = f"- {details.get('name')} {category_tag}"
        output.append(task_line)
    
    return "\n".join(output)

def generate_end_of_day_message():
    """Generate the end of day follow-up message"""
    today = datetime.now().strftime("%A, %B %d, %Y")
    tasks = get_todays_tasks()
    task_list = format_task_summary(tasks)
    
    message = f"""
🌆 End of Day Task Follow-up | {today}

Here are your tasks due today that aren't marked as complete:

{task_list}

Let me know which ones you've completed, and I'll update your Notion database. Any incomplete tasks will be rescheduled for the next business day.

Reply with task numbers that are complete, e.g., "1, 3, 4 complete" or "all complete" or "none complete".
"""
    return message, tasks

if __name__ == "__main__":
    message, tasks = generate_end_of_day_message()
    print(message)