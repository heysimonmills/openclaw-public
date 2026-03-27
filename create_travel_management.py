#!/usr/bin/env python3
import json
import requests
import os

# Load Notion API key
config_path = os.path.join(os.path.dirname(__file__), 'notion_config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

API_KEY = config['api_key']

# API Constants
NOTION_API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_travel_page():
    """Create a Travel Management page."""
    url = f"{NOTION_API}/pages"
    
    payload = {
        "parent": {
            "type": "database_id",
            "database_id": config['tasks_db_id'].replace('-', '')
        },
        "icon": {
            "type": "emoji",
            "emoji": "✈️"
        },
        "cover": {
            "type": "external",
            "external": {
                "url": "https://images.unsplash.com/photo-1488085061387-422e29b40080"
            }
        },
        "properties": {
            "Task name": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Travel Management"
                        }
                    }
                ]
            },
            "Task type": {
                "multi_select": [
                    {
                        "name": "🏠 Personal"
                    }
                ]
            },
            "Status": {
                "status": {
                    "name": "Not started"
                }
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
                            "text": {
                                "content": "Travel Management"
                            }
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
                            "text": {
                                "content": "Your central travel hub. Forward travel confirmations to your-assistant-email@gmail.com for automatic processing."
                            }
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
                            "text": {
                                "content": ""
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            page = response.json()
            print(f"Successfully created Travel Management page!")
            print(f"Page ID: {page.get('id')}")
            return page
        else:
            print(f"Error creating Travel page: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def create_travel_notes():
    """Create a text file with travel management instructions."""
    notes = """# Travel Management with Noah

## Getting Started
1. Forward all travel confirmations to: your-assistant-email@gmail.com
2. Include [TRAVEL] in the subject line for easier processing

## What Gets Tracked
- Flight confirmations & e-tickets
- Hotel/Airbnb bookings
- Rental car reservations
- Travel insurance
- Event tickets
- Visa/passport information

## Pre-Trip Support
- 7 days before: Packing checklist
- 3 days before: Booking verification
- 24 hours before: Check-in reminders

## During-Trip Support
- Daily morning briefing with agenda
- Weather alerts
- Important location information

## How to Ask for Help
Just message "Travel help: [your question]" and I'll assist with anything travel-related!

## Travel Document Storage
I'll keep copies of your important travel documents for easy retrieval when needed.
"""
    
    notes_path = os.path.join(os.path.dirname(__file__), 'travel_management.md')
    with open(notes_path, 'w') as f:
        f.write(notes)
    
    print(f"Created travel management notes at {notes_path}")
    return notes_path

def setup_travel_reminders():
    """Set up pre-trip reminder cron jobs."""
    # Set up the reminders
    reminders = [
        # Daily travel check
        {"name": "daily-travel-check", "schedule": {"kind": "cron", "expr": "0 9 * * *"}, 
         "payload": {"kind": "systemEvent", "text": "Check for upcoming travel in Simon's calendar and send reminders if needed."}, 
         "sessionTarget": "main", "enabled": True},
        
        # Pre-travel email
        {"name": "travel-email-processor", "schedule": {"kind": "cron", "expr": "0 10,14,18 * * *"}, 
         "payload": {"kind": "systemEvent", "text": "Process any travel confirmation emails in your-assistant-email@gmail.com inbox."}, 
         "sessionTarget": "main", "enabled": True}
    ]
    
    return reminders

if __name__ == "__main__":
    print("Setting up Travel Management system...")
    print("\n1. Creating Travel Management page in Notion...")
    page_result = create_travel_page()
    
    if page_result:
        print("\n2. Creating travel management notes...")
        notes_path = create_travel_notes()
        
        print("\n3. Setting up travel reminder system...")
        reminders = setup_travel_reminders()
        
        print("\n✅ Travel Management System Setup Complete!")
        print(f"\nTravel Management page: {page_result.get('url')}")
        print(f"Travel notes: {notes_path}")
        
        print("\nNext Steps:")
        print("1. Start forwarding travel confirmation emails to your-assistant-email@gmail.com")
        print("2. Add [TRAVEL] to the subject line for easier processing")
        print("3. I'll automatically extract travel details and keep your calendar updated")
    else:
        print("\n❌ Failed to set up Travel Management System.")