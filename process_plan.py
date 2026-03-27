#!/usr/bin/env python3
import json
import requests
import os
import sys
from datetime import datetime, timedelta
import re

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

def guess_category(task_text):
    """Guess the category of a task based on its content."""
    task_lower = task_text.lower()
    
    # Keywords for each category
    gsg_keywords = ["gsg", "client", "george st", "business", "consulting", "meeting", "pitch", "proposal"]
    gjc_keywords = ["gjc", "good jelly", "jelly", "product", "inventory", "packaging", "order", "collagen"]
    
    # Check for explicit category mentions
    if "gsg" in task_lower or any(keyword in task_lower for keyword in gsg_keywords):
        return "GSG"
    elif "gjc" in task_lower or any(keyword in task_lower for keyword in gjc_keywords):
        return "GJC"
    else:
        return "personal"

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
    if due_date:
        properties["Due date"] = {
            "date": {
                "start": due_date
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

def parse_plan_message(message_text, is_tomorrow=False):
    """Parse a plan message and extract tasks.
    
    Args:
        message_text: The text of the message
        is_tomorrow: Whether this plan is for tomorrow (True) or today (False)
    """
    # Get the target date
    today = datetime.now()
    if is_tomorrow:
        target_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        target_date = today.strftime("%Y-%m-%d")
    
    # Split the message into lines
    lines = message_text.strip().split('\n')
    
    # Remove the first line if it's the "plan for today" or "tomorrow's plan" header
    if lines and ("plan for today" in lines[0].lower() or "tomorrow's plan" in lines[0].lower()):
        lines = lines[1:]
    
    tasks = []
    
    # Process each line as a potential task
    for line in lines:
        # Skip empty lines
        line = line.strip()
        if not line:
            continue
        
        # Look for category markers
        category = None
        
        # Check for explicit category tags
        if "(GSG)" in line or "[GSG]" in line:
            category = "GSG"
            # Remove the tag from the task name
            line = re.sub(r'\s*[\(\[]GSG[\)\]]\s*', ' ', line).strip()
        elif "(GJC)" in line or "[GJC]" in line:
            category = "GJC"
            # Remove the tag from the task name
            line = re.sub(r'\s*[\(\[]GJC[\)\]]\s*', ' ', line).strip()
        elif "(personal)" in line.lower() or "[personal]" in line.lower():
            category = "personal"
            # Remove the tag from the task name
            line = re.sub(r'\s*[\(\[]personal[\)\]]\s*', ' ', line, flags=re.IGNORECASE).strip()
        
        # If no explicit category, guess based on content
        if not category:
            category = guess_category(line)
        
        # Add to tasks list
        tasks.append({
            "name": line,
            "category": category,
            "due_date": target_date
        })
    
    return tasks

def process_plan(message_text, is_tomorrow=False):
    """Process a plan message and add tasks to Notion."""
    tasks = parse_plan_message(message_text, is_tomorrow)
    
    # Add all tasks and collect results
    results = []
    for task in tasks:
        result = create_task(
            task_name=task["name"],
            category=task["category"],
            due_date=task.get("due_date")
        )
        results.append(result)
    
    # Generate summary
    success_count = sum(1 for r in results if r.get("success", False))
    summary = f"Added {success_count} tasks to Notion for {'tomorrow' if is_tomorrow else 'today'}."
    
    # List the tasks that were added
    task_list = []
    for i, result in enumerate(results, 1):
        if result.get("success", False):
            task_list.append(f"{i}. {result.get('task_name', 'Unknown task')}")
    
    # Return the summary and task list
    return summary, task_list

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        message_text = sys.argv[1]
        is_tomorrow = len(sys.argv) > 2 and sys.argv[2].lower() == "tomorrow"
        
        summary, task_list = process_plan(message_text, is_tomorrow)
        print(summary)
        print("\n".join(task_list))