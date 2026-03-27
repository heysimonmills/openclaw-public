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
TASKS_DB_ID = config['tasks_db_id']

# API Constants
NOTION_API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_parent_page_id():
    """Get the parent page ID of the existing tasks database."""
    
    url = f"{NOTION_API}/databases/{TASKS_DB_ID}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            database = response.json()
            parent = database.get('parent', {})
            
            # Check if parent is workspace or page
            if parent.get('type') == 'page':
                return parent.get('page_id')
            elif parent.get('type') == 'workspace':
                # We need a page ID, not workspace
                return None
                
        print(f"Error getting tasks database: {response.status_code}")
        print(response.text)
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def create_travel_page():
    """Create a Travel Management page."""
    
    parent_id = get_parent_page_id()
    
    if not parent_id:
        print("Could not determine parent page ID")
        
        # Try to create the page in workspace instead
        parent = {"type": "workspace", "workspace": True}
    else:
        parent = {"type": "page", "page_id": parent_id}
    
    url = f"{NOTION_API}/pages"
    
    payload = {
        "parent": parent,
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
            "title": {
                "title": [
                    {
                        "text": {
                            "content": "Travel Management"
                        }
                    }
                ]
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
                                "content": "A central place to manage all your travel information."
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
            return page
        else:
            print(f"Error creating Travel page: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def create_travel_database(parent_page_id):
    """Create a travel database in Notion under the parent page."""
    
    url = f"{NOTION_API}/databases"
    
    payload = {
        "parent": {
            "type": "page_id",
            "page_id": parent_page_id
        },
        "icon": {
            "type": "emoji",
            "emoji": "🧳"
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Trips"
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
            "Total Cost": {
                "number": {
                    "format": "dollar"
                }
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Successfully created Trips database!")
            print(f"Database ID: {result.get('id')}")
            
            # Save the database ID
            trips_db_id = result.get('id')
            
            # Now create the Flights database
            create_flights_database(parent_page_id, trips_db_id)
            
            # Create the Accommodations database
            create_accommodations_database(parent_page_id, trips_db_id)
                
            return result
        else:
            print(f"Error creating Trips database: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return None

def create_flights_database(parent_page_id, trips_db_id):
    """Create a flights database in Notion under the parent page."""
    
    url = f"{NOTION_API}/databases"
    
    payload = {
        "parent": {
            "type": "page_id",
            "page_id": parent_page_id
        },
        "icon": {
            "type": "emoji",
            "emoji": "✈️"
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Flights"
                }
            }
        ],
        "properties": {
            "Flight": {
                "title": {}
            },
            "Trip": {
                "relation": {
                    "database_id": trips_db_id,
                    "single_property": {}
                }
            },
            "Airline": {
                "select": {
                    "options": [
                        {"name": "Air Canada", "color": "red"},
                        {"name": "WestJet", "color": "blue"},
                        {"name": "United", "color": "blue"},
                        {"name": "Delta", "color": "red"},
                        {"name": "American", "color": "blue"},
                        {"name": "Other", "color": "gray"}
                    ]
                }
            },
            "Flight Number": {
                "rich_text": {}
            },
            "Departure Date": {
                "date": {}
            },
            "Departure Airport": {
                "rich_text": {}
            },
            "Arrival Airport": {
                "rich_text": {}
            },
            "Booking Reference": {
                "rich_text": {}
            },
            "Confirmation": {
                "rich_text": {}
            },
            "Seat": {
                "rich_text": {}
            },
            "Price": {
                "number": {
                    "format": "dollar"
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Booked", "color": "blue"},
                        {"name": "Checked In", "color": "green"},
                        {"name": "Completed", "color": "gray"},
                        {"name": "Cancelled", "color": "red"},
                        {"name": "Delayed", "color": "yellow"}
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
            print(f"Successfully created Flights database!")
            print(f"Database ID: {result.get('id')}")
            
            # Save the database ID
            flights_db_id = result.get('id')
            
            # Save all database IDs
            travel_config = {
                "trips_db_id": trips_db_id,
                "flights_db_id": flights_db_id
            }
                
            return result
        else:
            print(f"Error creating Flights database: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error creating Flights database: {str(e)}")
        return None

def create_accommodations_database(parent_page_id, trips_db_id):
    """Create an accommodations database in Notion under the parent page."""
    
    url = f"{NOTION_API}/databases"
    
    payload = {
        "parent": {
            "type": "page_id",
            "page_id": parent_page_id
        },
        "icon": {
            "type": "emoji",
            "emoji": "🏨"
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Accommodations"
                }
            }
        ],
        "properties": {
            "Name": {
                "title": {}
            },
            "Trip": {
                "relation": {
                    "database_id": trips_db_id,
                    "single_property": {}
                }
            },
            "Type": {
                "select": {
                    "options": [
                        {"name": "Hotel", "color": "blue"},
                        {"name": "Airbnb", "color": "orange"},
                        {"name": "Friend/Family", "color": "green"},
                        {"name": "Other", "color": "gray"}
                    ]
                }
            },
            "Check-in Date": {
                "date": {}
            },
            "Check-out Date": {
                "date": {}
            },
            "Address": {
                "rich_text": {}
            },
            "Booking Reference": {
                "rich_text": {}
            },
            "Confirmation": {
                "rich_text": {}
            },
            "Price": {
                "number": {
                    "format": "dollar"
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Booked", "color": "blue"},
                        {"name": "Checked In", "color": "green"},
                        {"name": "Completed", "color": "gray"},
                        {"name": "Cancelled", "color": "red"}
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
            print(f"Successfully created Accommodations database!")
            print(f"Database ID: {result.get('id')}")
            
            # Save the database ID
            accom_db_id = result.get('id')
            
            # Save all database IDs
            travel_config = {
                "trips_db_id": trips_db_id,
                "flights_db_id": None,  # Should be set by flights function
                "accommodations_db_id": accom_db_id
            }
            
            with open(os.path.join(os.path.dirname(__file__), 'travel_config.json'), 'w') as f:
                json.dump(travel_config, f)
                
            return result
        else:
            print(f"Error creating Accommodations database: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error creating Accommodations database: {str(e)}")
        return None

if __name__ == "__main__":
    print("Creating Travel Management page...")
    page_result = create_travel_page()
    
    if page_result:
        page_id = page_result.get('id')
        print(f"Travel page created! ID: {page_id}")
        print(f"URL: {page_result.get('url')}")
        
        print("\nCreating Travel databases...")
        db_result = create_travel_database(page_id)
        
        if db_result:
            print("\nTravel Management system created successfully!")
            print(f"Access your travel workspace here: {page_result.get('url')}")
        else:
            print("\nFailed to create travel databases.")
    else:
        print("Failed to create Travel Management page.")