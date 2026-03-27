#!/usr/bin/env python3
import json
import requests
import os
import sys

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

def create_travel_database():
    """Create a travel database in Notion."""
    
    # First, find the user's workspace ID
    search_url = f"{NOTION_API}/search"
    search_payload = {
        "filter": {
            "value": "page",
            "property": "object"
        },
        "page_size": 1
    }
    
    try:
        response = requests.post(search_url, headers=HEADERS, json=search_payload)
        if response.status_code != 200:
            print(f"Error searching for workspace: {response.status_code}")
            print(response.text)
            return None
            
        # Get the first page to get the workspace ID
        results = response.json().get('results', [])
        if not results:
            print("No pages found to determine workspace ID")
            return None
            
        # Extract workspace ID from the parent property
        first_page = results[0]
        workspace_id = None
        
        if first_page.get('parent', {}).get('type') == 'workspace':
            workspace_id = True  # Just need to know it's a workspace parent
        else:
            print("Could not determine workspace ID")
            return None
    except Exception as e:
        print(f"Error determining workspace ID: {str(e)}")
        return None
    
    # Now create the database in the workspace
    url = f"{NOTION_API}/databases"
    
    payload = {
        "parent": {
            "type": "workspace",
            "workspace": True
        },
        "icon": {
            "type": "emoji",
            "emoji": "✈️"
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Travel Management",
                    "link": None
                }
            }
        ],
        "description": [
            {
                "type": "text",
                "text": {
                    "content": "Track all trips, flights, accommodations, and travel details",
                    "link": None
                }
            }
        ],
        "properties": {
            "Trip Name": {
                "title": {}
            },
            "Trip Type": {
                "select": {
                    "options": [
                        {"name": "Business", "color": "blue"},
                        {"name": "Personal", "color": "green"},
                        {"name": "GJC", "color": "yellow"},
                        {"name": "GSG", "color": "red"}
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Planning", "color": "gray"},
                        {"name": "Booked", "color": "blue"},
                        {"name": "In Progress", "color": "yellow"},
                        {"name": "Completed", "color": "green"},
                        {"name": "Cancelled", "color": "red"}
                    ]
                }
            },
            "Start Date": {
                "date": {}
            },
            "End Date": {
                "date": {}
            },
            "Origin": {
                "rich_text": {}
            },
            "Destination": {
                "rich_text": {}
            },
            "Flight Details": {
                "rich_text": {}
            },
            "Accommodation": {
                "rich_text": {}
            },
            "Confirmation Numbers": {
                "rich_text": {}
            },
            "Total Cost": {
                "number": {
                    "format": "dollar"
                }
            },
            "Currency": {
                "select": {
                    "options": [
                        {"name": "CAD", "color": "red"},
                        {"name": "USD", "color": "blue"},
                        {"name": "EUR", "color": "green"},
                        {"name": "GBP", "color": "purple"},
                        {"name": "Other", "color": "gray"}
                    ]
                }
            },
            "Notes": {
                "rich_text": {}
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Successfully created travel database!")
            print(f"Database ID: {result.get('id')}")
            
            # Save the database ID
            travel_config = {"travel_db_id": result.get('id')}
            with open(os.path.join(os.path.dirname(__file__), 'travel_config.json'), 'w') as f:
                json.dump(travel_config, f)
                
            return result
        else:
            print(f"Error creating database: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return None

if __name__ == "__main__":
    result = create_travel_database()
    
    if result:
        print("Travel database created successfully!")
        print(f"URL: {result.get('url')}")
    else:
        print("Failed to create travel database.")