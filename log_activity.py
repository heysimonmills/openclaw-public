#!/usr/bin/env python3
"""
Activity Logger
Log activities to the activity log for dashboard tracking
"""

import json
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

# Toronto timezone
EST = ZoneInfo('America/Toronto')

ACTIVITY_LOG = "/home/ubuntu/clawd/data/activity-log.jsonl"

def log_activity(category, title, description, cost=0.0, duration_seconds=0, metadata=None):
    """
    Log an activity to the activity log
    
    Categories: system, email, task, conversation, research, development, notion, travel, reminder
    """
    activity = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(EST).isoformat(),
        "category": category,
        "title": title,
        "description": description,
        "status": "completed",
        "cost": cost,
        "duration_seconds": duration_seconds
    }
    
    if metadata:
        activity["metadata"] = metadata
    
    with open(ACTIVITY_LOG, 'a') as f:
        f.write(json.dumps(activity) + '\n')
    
    return activity

# Convenience functions for common activities
def log_heartbeat(description="No new activity"):
    return log_activity("system", "Heartbeat check", description)

def log_email_check(new_emails=0):
    desc = f"{new_emails} new emails" if new_emails > 0 else "No new emails"
    return log_activity("email", "Email check", desc)

def log_task_completed(task_name):
    return log_activity("task", f"Completed: {task_name}", f"Task '{task_name}' marked as done")

def log_conversation(summary):
    return log_activity("conversation", "Chat", summary)

def log_development(feature, details):
    return log_activity("development", f"Development: {feature}", details)

def log_notion_operation(operation, details):
    return log_activity("notion", f"Notion: {operation}", details)

def log_research(topic, findings):
    return log_activity("research", f"Research: {topic}", findings)

def log_travel_update(destination, days_until):
    return log_activity("travel", f"Travel check: {destination}", f"{days_until} days until trip")

if __name__ == "__main__":
    # Test logging
    log_activity("system", "Activity logger test", "Testing the activity logging system")
    print("Activity logged successfully!")
