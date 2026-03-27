#!/usr/bin/env python3
import json
import requests
import os
import sys
from datetime import datetime, timezone

# Load config
config_path = os.path.join(os.path.dirname(__file__), 'notion_config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

API_KEY = config['api_key']
DATABASE_ID = config['tasks_db_id'].replace('-', '')  # Remove dashes for API compatibility

# API Constants
NOTION_API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"  # Using stable version
}

def query_database(filter_params=None):
    """Query the tasks database with optional filters."""
    url = f"{NOTION_API}/databases/{DATABASE_ID}/query"
    
    payload = {}
    if filter_params:
        payload = filter_params
        
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error querying database: {response.status_code}")
        print(response.text)
        return None

def create_task(task_name, status="Not started", priority=None, due_date=None, description=None, task_type=None):
    """Create a new task in the database."""
    url = f"{NOTION_API}/pages"
    
    # Build properties object
    properties = {
        "Task name": {"title": [{"text": {"content": task_name}}]},
        "Status": {"status": {"name": status}}
    }
    
    # Add optional properties if provided
    if priority:
        properties["Priority"] = {"select": {"name": priority}}
    
    if due_date:
        # Format: 2022-12-31 or 2022-12-31T10:00:00Z
        properties["Due date"] = {"date": {"start": due_date}}
    
    if task_type and isinstance(task_type, list):
        properties["Task type"] = {"multi_select": [{"name": t} for t in task_type]}
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
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
                            "text": {"content": description}
                        }
                    ]
                }
            }
        ]
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating task: {response.status_code}")
        print(response.text)
        return None

def update_task(page_id, properties=None, description=None):
    """Update an existing task by page ID."""
    url = f"{NOTION_API}/pages/{page_id}"
    
    payload = {}
    if properties:
        payload["properties"] = properties
    
    response = requests.patch(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        # If description update is requested, handle separately
        if description:
            update_description(page_id, description)
        return response.json()
    else:
        print(f"Error updating task: {response.status_code}")
        print(response.text)
        return None

def update_description(page_id, description):
    """Update the content/description of a task."""
    url = f"{NOTION_API}/blocks/{page_id}/children"
    
    payload = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": description}
                        }
                    ]
                }
            }
        ]
    }
    
    response = requests.patch(url, headers=HEADERS, json=payload)
    return response.status_code == 200

def get_task_by_name(name, partial_match=True):
    """Find a task by name (exact or partial match)."""
    url = f"{NOTION_API}/databases/{DATABASE_ID}/query"
    
    # For exact match
    if not partial_match:
        payload = {
            "filter": {
                "property": "Task name",
                "title": {
                    "equals": name
                }
            }
        }
    else:
        # For partial match (contains)
        payload = {
            "filter": {
                "property": "Task name",
                "title": {
                    "contains": name
                }
            }
        }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])
    else:
        print(f"Error searching for task: {response.status_code}")
        print(response.text)
        return []

def get_tasks_by_status(status):
    """Get all tasks with a specific status."""
    url = f"{NOTION_API}/databases/{DATABASE_ID}/query"
    
    payload = {
        "filter": {
            "property": "Status",
            "status": {
                "equals": status
            }
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
        data = response.json()
        return data.get('results', [])
    else:
        print(f"Error getting tasks by status: {response.status_code}")
        print(response.text)
        return []

def get_tasks_by_priority(priority):
    """Get all tasks with a specific priority."""
    url = f"{NOTION_API}/databases/{DATABASE_ID}/query"
    
    payload = {
        "filter": {
            "property": "Priority",
            "select": {
                "equals": priority
            }
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
        data = response.json()
        return data.get('results', [])
    else:
        print(f"Error getting tasks by priority: {response.status_code}")
        print(response.text)
        return []

def get_due_tasks(days=7):
    """Get tasks due within the specified number of days."""
    # Not implemented - requires date filtering logic
    pass

def get_tasks_due_today():
    """Get tasks due today or overdue (not done)."""
    from datetime import datetime, date
    
    today = date.today().isoformat()
    
    url = f"{NOTION_API}/databases/{DATABASE_ID}/query"
    
    # Query for tasks NOT done (status != Done) with due date <= today
    payload = {
        "filter": {
            "and": [
                {
                    "property": "Status",
                    "status": {
                        "does_not_equal": "Done"
                    }
                },
                {
                    "property": "Due date",
                    "date": {
                        "on_or_before": today
                    }
                }
            ]
        },
        "sorts": [
            {"property": "Due date", "direction": "ascending"},
            {"property": "Priority", "direction": "descending"}
        ]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])
    else:
        print(f"Error getting due tasks: {response.status_code}")
        print(response.text)
        return []

def get_overdue_tasks():
    """Get overdue tasks (due date before today, not done)."""
    from datetime import date
    
    today = date.today().isoformat()
    
    url = f"{NOTION_API}/databases/{DATABASE_ID}/query"
    
    payload = {
        "filter": {
            "and": [
                {
                    "property": "Status",
                    "status": {
                        "does_not_equal": "Done"
                    }
                },
                {
                    "property": "Due date",
                    "date": {
                        "before": today
                    }
                }
            ]
        },
        "sorts": [
            {"property": "Due date", "direction": "ascending"}
        ]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get('results', [])
    else:
        print(f"Error getting overdue tasks: {response.status_code}")
        print(response.text)
        return []

def format_tasks_for_brief(tasks):
    """Format tasks for morning brief with categories and priorities."""
    if not tasks:
        return "None 🎉"
    
    output = []
    for task in tasks:
        details = extract_task_details(task)
        name = details.get('name', 'Untitled')
        status = details.get('status', '')
        priority = details.get('priority', '')
        due = details.get('due_date', '')
        task_types = details.get('task_types', [])
        
        # Get category emoji
        category = ""
        for t in task_types:
            if "GJC" in t:
                category = "🍯"
            elif "GSG" in t:
                category = "💼"
            elif "Personal" in t:
                category = "🏠"
        
        # Priority indicator
        priority_marker = ""
        if priority == "High":
            priority_marker = " **[HIGH]**"
        elif priority == "Medium":
            priority_marker = " [med]"
        
        # Overdue indicator
        from datetime import date
        if due and due < date.today().isoformat():
            days_overdue = (date.today() - date.fromisoformat(due)).days
            due_str = f" *(overdue {days_overdue}d)*"
        else:
            due_str = ""
        
        output.append(f"• {category} {name}{priority_marker}{due_str}")
    
    return "\n".join(output)

def extract_task_details(task):
    """Extract readable details from a task object."""
    details = {
        "id": task.get("id"),
        "url": task.get("url")
    }
    
    properties = task.get("properties", {})
    
    # Extract title
    title_prop = properties.get("Task name", {})
    title = ""
    if "title" in title_prop:
        title_objects = title_prop.get("title", [])
        title = "".join([t.get("plain_text", "") for t in title_objects])
    details["name"] = title
    
    # Extract status
    status_prop = properties.get("Status", {})
    if "status" in status_prop and status_prop["status"]:
        details["status"] = status_prop["status"].get("name", "Unknown")
    
    # Extract priority
    priority_prop = properties.get("Priority", {})
    if "select" in priority_prop and priority_prop["select"]:
        details["priority"] = priority_prop["select"].get("name", "")
    
    # Extract due date
    date_prop = properties.get("Due date", {})
    if "date" in date_prop and date_prop["date"]:
        details["due_date"] = date_prop["date"].get("start", "")
    
    # Extract task types (multi-select)
    type_prop = properties.get("Task type", {})
    if "multi_select" in type_prop:
        types = type_prop.get("multi_select", [])
        details["task_types"] = [t.get("name", "") for t in types]
    
    # Extract description - would need a separate API call to get content
    # This would need to be implemented if needed
    
    return details

def format_tasks_list(tasks):
    """Format a list of tasks into a readable string."""
    if not tasks:
        return "No tasks found."
    
    output = []
    for i, task in enumerate(tasks, 1):
        details = extract_task_details(task)
        task_line = f"{i}. {details.get('name', 'Untitled')}"
        
        # Add status if available
        if "status" in details:
            task_line += f" - {details.get('status')}"
        
        # Add priority if available
        if "priority" in details:
            task_line += f" (Priority: {details.get('priority')})"
        
        # Add due date if available
        if "due_date" in details:
            task_line += f" - Due: {details.get('due_date')}"
            
        output.append(task_line)
    
    return "\n".join(output)

# Category mapping - shortcuts to full emoji names
CATEGORY_MAP = {
    "GSG": "💼 GSG",
    "GJC": "🍯 GJC",
    "Personal": "🏠 Personal",
    "gsg": "💼 GSG",
    "gjc": "🍯 GJC",
    "personal": "🏠 Personal"
}

def parse_category(category_input):
    """Convert category shorthand to full name."""
    if category_input in CATEGORY_MAP:
        return CATEGORY_MAP[category_input]
    return category_input  # Return as-is if not in map

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            # Default: list all tasks
            results = query_database()
            if results:
                print(format_tasks_list(results.get("results", [])))
            
        elif command == "list-status" and len(sys.argv) > 2:
            # List tasks by status
            status = sys.argv[2]
            results = get_tasks_by_status(status)
            print(f"Tasks with status '{status}':")
            print(format_tasks_list(results))
            
        elif command == "add" and len(sys.argv) > 2:
            # Add a new task
            # Usage: add <name> [category] [status] [priority] [due_date]
            task_name = sys.argv[2]
            
            category = None
            if len(sys.argv) > 3 and sys.argv[3] in ["GSG", "GJC", "Personal", "gsg", "gjc", "personal"]:
                category = [parse_category(sys.argv[3])]
            
            status = "Not started"
            if len(sys.argv) > 4:
                status = sys.argv[4]
            
            priority = None
            if len(sys.argv) > 5:
                priority = sys.argv[5]
            
            due_date = None
            if len(sys.argv) > 6:
                due_date = sys.argv[6]
            
            result = create_task(task_name, status, priority, due_date, task_type=category)
            if result:
                cat_str = f" ({category[0]})" if category else ""
                print(f"Created task: {task_name}{cat_str}")
            
        elif command == "update-status" and len(sys.argv) > 3:
            # Update task status
            task_name = sys.argv[2]
            new_status = sys.argv[3]
            
            tasks = get_task_by_name(task_name)
            if tasks:
                task = tasks[0]
                page_id = task.get("id")
                update_result = update_task(page_id, {
                    "Status": {"status": {"name": new_status}}
                })
                if update_result:
                    print(f"Updated status of '{task_name}' to {new_status}")
            else:
                print(f"Task '{task_name}' not found")
        
        elif command == "update-category" and len(sys.argv) > 3:
            # Update task category
            task_name = sys.argv[2]
            category = parse_category(sys.argv[3])
            
            tasks = get_task_by_name(task_name)
            if tasks:
                task = tasks[0]
                page_id = task.get("id")
                update_result = update_task(page_id, {
                    "Task type": {"multi_select": [{"name": category}]}
                })
                if update_result:
                    print(f"Updated category of '{task_name}' to {category}")
            else:
                print(f"Task '{task_name}' not found")
        
        elif command == "update-due" and len(sys.argv) > 3:
            # Update task due date
            task_name = sys.argv[2]
            due_date = sys.argv[3]
            
            tasks = get_task_by_name(task_name)
            if tasks:
                task = tasks[0]
                page_id = task.get("id")
                update_result = update_task(page_id, {
                    "Due date": {"date": {"start": due_date}}
                })
                if update_result:
                    print(f"Updated due date of '{task_name}' to {due_date}")
            else:
                print(f"Task '{task_name}' not found")
        
        elif command == "update-name" and len(sys.argv) > 3:
            # Update task name
            task_name = sys.argv[2]
            new_name = sys.argv[3]
            
            tasks = get_task_by_name(task_name)
            if tasks:
                task = tasks[0]
                page_id = task.get("id")
                update_result = update_task(page_id, {
                    "Task name": {"title": [{"text": {"content": new_name}}]}
                })
                if update_result:
                    print(f"Updated task name from '{task_name}' to '{new_name}'")
            else:
                print(f"Task '{task_name}' not found")
        
        elif command == "due-today":
            # Get tasks due today
            due_tasks = get_tasks_due_today()
            if due_tasks:
                print(format_tasks_for_brief(due_tasks))
            else:
                print("None 🎉")
        
        elif command == "overdue":
            # Get overdue tasks
            overdue = get_overdue_tasks()
            if overdue:
                print(format_tasks_for_brief(overdue))
            else:
                print("None 🎉")
        
        elif command == "brief":
            # Full morning brief output
            due_tasks = get_tasks_due_today()
            overdue = get_overdue_tasks()
            
            print("📋 Tasks Due Today:")
            if due_tasks:
                print(format_tasks_for_brief(due_tasks))
            else:
                print("None 🎉")
            
            if overdue:
                print("\n⚠️ Overdue:")
                print(format_tasks_for_brief(overdue))
        
        elif command == "help":
            print("Usage:")
            print("  list - List all tasks")
            print("  list-status <status> - List tasks with specified status")
            print("  due-today - List tasks due today")
            print("  overdue - List overdue overdue tasks")
            print("  brief - Morning brief format (due today + overdue)")
            print("  add <name> [category] [status] [priority] [due_date] - Add a new task")
            print("    Categories: GSG, GJC, Personal")
            print("  update-status <name> <status> - Update task status")
            print("  update-category <name> <category> - Update task category")
            print("  update-due <name> <due_date> - Update task due date (YYYY-MM-DD)")
            print("  update-name <name> <new_name> - Update task name")
    else:
        print("No command specified. Try 'help' for available commands.")