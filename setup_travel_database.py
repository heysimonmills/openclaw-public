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

def create_travel_database():
    """Create a travel database in Notion workspace."""
    
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
        "cover": {
            "type": "external",
            "external": {
                "url": "https://images.unsplash.com/photo-1488085061387-422e29b40080"
            }
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Travel Management"
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
            "Departure Date": {
                "date": {}
            },
            "Return Date": {
                "date": {}
            },
            "Origin": {
                "rich_text": {}
            },
            "Destination": {
                "rich_text": {}
            },
            "Flight Info": {
                "rich_text": {}
            },
            "Accommodation": {
                "rich_text": {}
            },
            "Confirmation #": {
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
            "Documents": {
                "files": {}
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
            print(f"Successfully created Travel Management database!")
            print(f"Database ID: {result.get('id')}")
            print(f"URL: {result.get('url')}")
            
            # Save the database ID for future use
            travel_config = {
                "travel_db_id": result.get('id')
            }
            
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
    print("Creating Travel Management database in Notion...")
    result = create_travel_database()
    
    if result:
        print("\n✅ Travel Management Database Setup Complete!")
        print(f"\nTravel Database URL: {result.get('url')}")
    else:
        print("\n❌ Failed to set up Travel Management Database.")