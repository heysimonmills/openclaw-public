#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from datetime import datetime, timedelta

def add_task(task_name, category, due_date=None, priority=None, notes=None):
    """Add a new task to Notion with category in the Task type field"""
    
    # Convert category to task types expected by the Notion database
    category_mapping = {
        "GSG": ["💼 GSG"],
        "GJC": ["🍯 GJC"],
        "personal": ["🏠 Personal"]
    }
    
    task_type = category_mapping.get(category.upper(), ["🏠 Personal"])
    
    # Convert relative dates to actual dates
    if due_date:
        today = datetime.now()
        if due_date.lower() == "today":
            actual_date = today.strftime("%Y-%m-%d")
        elif due_date.lower() == "tomorrow":
            actual_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "next week" in due_date.lower():
            actual_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")
        else:
            actual_date = due_date
    else:
        actual_date = None
    
    # First check if we have the required task types in the database
    # If not, try to create them first (although API doesn't fully support this)
    
    # Now create the task using notion_tasks.py
    task_script = os.path.join(os.path.dirname(__file__), 'notion_tasks.py')
    
    # Prepare command with available details
    command = [sys.executable, task_script, "add", task_name]
    if due_date:
        command.extend(["--due", actual_date])
    if priority:
        command.extend(["--priority", priority])
    if category:
        command.extend(["--type", json.dumps(task_type)])
    if notes:
        command.extend(["--notes", notes])
    
    # Execute the command
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error adding task: {str(e)}"

def guess_category(task_description):
    """Make an educated guess about the category of a task"""
    
    # Keywords that might indicate business/GSG tasks
    gsg_keywords = [
        "client", "meeting", "proposal", "business", "marketing", 
        "consulting", "strategy", "george st", "georgest", "gsg",
        "presentation", "report", "call", "email client", "invoice"
    ]
    
    # Keywords that might indicate Good Jelly Co tasks
    gjc_keywords = [
        "jelly", "product", "inventory", "order", "shipping", 
        "collagen", "candy", "packaging", "supplier", "manufacturer",
        "sales", "gjc", "good jelly", "sample", "ingredient"
    ]
    
    # Keywords that might indicate personal tasks
    personal_keywords = [
        "gym", "workout", "exercise", "groceries", "shopping",
        "home", "apartment", "family", "friend", "date", "ian",
        "water polo", "cycling", "birthday", "personal", "health"
    ]
    
    # Normalize the description
    description = task_description.lower()
    
    # Count matches for each category
    gsg_score = sum(1 for keyword in gsg_keywords if keyword.lower() in description)
    gjc_score = sum(1 for keyword in gjc_keywords if keyword.lower() in description)
    personal_score = sum(1 for keyword in personal_keywords if keyword.lower() in description)
    
    # Determine the most likely category
    if gsg_score > gjc_score and gsg_score > personal_score:
        return "GSG"
    elif gjc_score > gsg_score and gjc_score > personal_score:
        return "GJC"
    else:
        return "personal"
    
if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        task_name = sys.argv[1]
        category = sys.argv[2] if len(sys.argv) > 2 else guess_category(task_name)
        due_date = sys.argv[3] if len(sys.argv) > 3 else None
        priority = sys.argv[4] if len(sys.argv) > 4 else None
        
        result = add_task(task_name, category, due_date, priority)
        print(result)