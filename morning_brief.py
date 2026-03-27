#!/usr/bin/env python3
import sys
import os
import json
import requests
from datetime import datetime, timedelta, timezone
import subprocess

# Path to Notion tasks script
NOTION_TASKS_SCRIPT = os.path.join(os.path.dirname(__file__), 'notion_tasks.py')

def get_today_tasks():
    """Get tasks due today from Notion"""
    try:
        # We'll implement this using the tasks script later
        # For now, let's use a basic approach to list all tasks
        result = subprocess.run(
            [sys.executable, NOTION_TASKS_SCRIPT, "list"],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return f"Error getting tasks: {str(e)}"

def get_weather():
    """Get today's weather for Toronto"""
    try:
        result = subprocess.run(
            ["curl", "-s", "wttr.in/Toronto?format=3"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error getting weather: {str(e)}"

def get_calendar_events():
    """Get today's calendar events"""
    try:
        # Path to calendar checking script
        calendar_script = os.path.join(os.path.dirname(__file__), 'fixed_check_calendar.py')
        result = subprocess.run(
            [sys.executable, calendar_script],
            capture_output=True,
            text=True
        )
        
        # Extract just the events part from the output
        output = result.stdout
        return output
    except Exception as e:
        return f"Error checking calendar: {str(e)}"

def get_emails():
    """Check for new emails that need attention"""
    try:
        # Path to email checking script
        email_script = os.path.join(os.path.dirname(__file__), 'fixed_check_email.py')
        result = subprocess.run(
            [sys.executable, email_script],
            capture_output=True,
            text=True
        )
        
        # Extract the emails part from the output
        output = result.stdout
        return output
    except Exception as e:
        return f"Error checking emails: {str(e)}"

def generate_morning_brief():
    """Generate the complete morning brief"""
    today = datetime.now().strftime("%A, %B %d, %Y")
    
    # Get all the components
    weather = get_weather()
    tasks = get_today_tasks()
    calendar_events = get_calendar_events()
    emails = get_emails()
    
    # Build the brief
    brief = f"""
🌅 Good morning, Simon! | {today}

🌤️ WEATHER:
{weather}

📋 TODAY'S TASKS:
{tasks}

📅 TODAY'S SCHEDULE:
{calendar_events}

📬 EMAILS NEEDING ATTENTION:
{emails}

Have a productive day!
"""
    return brief

if __name__ == "__main__":
    brief = generate_morning_brief()
    print(brief)