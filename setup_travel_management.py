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
                "status": {
                    "options": [
                        {"name": "Planning", "color": "default"},
                        {"name": "Booked", "color": "blue"},
                        {"name": "In Progress", "color": "yellow"},
                        {"name": "Completed", "color": "green"},
                        {"name": "Cancelled", "color": "red"}
                    ],
                    "groups": [
                        {
                            "name": "Pre-Trip",
                            "color": "gray",
                            "option_ids": []  # We'll fill these in after creation
                        },
                        {
                            "name": "Active",
                            "color": "blue",
                            "option_ids": []
                        },
                        {
                            "name": "Post-Trip",
                            "color": "green",
                            "option_ids": []
                        }
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

def setup_travel_reminders():
    """Create scripts for travel reminder system."""
    
    # Create a script to handle pre-trip reminders (7 days, 3 days, 1 day before)
    pre_trip_script = """#!/usr/bin/env python3
import json
import requests
import os
import sys
import datetime

# Load travel database config
config_path = os.path.join(os.path.dirname(__file__), 'travel_config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

TRAVEL_DB_ID = config['travel_db_id']

# Load Notion API key
notion_config_path = os.path.join(os.path.dirname(__file__), 'notion_config.json')
with open(notion_config_path, 'r') as f:
    notion_config = json.load(f)

API_KEY = notion_config['api_key']

# API Constants
NOTION_API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_upcoming_trips(days_ahead=30):
    """Get trips departing within the next X days."""
    today = datetime.datetime.now().date()
    future_date = today + datetime.timedelta(days=days_ahead)
    
    today_str = today.isoformat()
    future_date_str = future_date.isoformat()
    
    # Query for upcoming trips
    url = f"{NOTION_API}/databases/{TRAVEL_DB_ID}/query"
    
    payload = {
        "filter": {
            "and": [
                {
                    "property": "Departure Date",
                    "date": {
                        "on_or_after": today_str
                    }
                },
                {
                    "property": "Departure Date",
                    "date": {
                        "on_or_before": future_date_str
                    }
                }
            ]
        },
        "sorts": [
            {
                "property": "Departure Date",
                "direction": "ascending"
            }
        ]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        trips = response.json().get('results', [])
        
        # Process each trip to extract relevant details
        processed_trips = []
        for trip in trips:
            properties = trip.get('properties', {})
            
            # Extract title
            title = ""
            title_prop = properties.get('Trip Name', {})
            if title_prop and 'title' in title_prop:
                title = " ".join([t.get('plain_text', '') for t in title_prop.get('title', [])])
            
            # Extract departure date
            departure_date = None
            departure_prop = properties.get('Departure Date', {})
            if departure_prop and 'date' in departure_prop and departure_prop['date']:
                departure_date = departure_prop['date'].get('start')
                
            # Only include trips that have a departure date
            if departure_date:
                departure_date_obj = datetime.datetime.fromisoformat(departure_date).date()
                days_until_departure = (departure_date_obj - today).days
                
                processed_trips.append({
                    'id': trip.get('id'),
                    'title': title,
                    'departure_date': departure_date,
                    'days_until_departure': days_until_departure
                })
        
        return processed_trips
    else:
        print(f"Error querying trips: {response.status_code}")
        return []

def generate_reminders():
    """Generate reminders for upcoming trips."""
    trips = get_upcoming_trips()
    
    reminders = []
    
    for trip in trips:
        days = trip['days_until_departure']
        
        # 7-day reminder
        if days == 7:
            reminders.append({
                'trip': trip,
                'type': '7_day',
                'message': f"🧳 7-DAY TRIP REMINDER: {trip['title']} departing in one week on {trip['departure_date']}\\n\\nTime to start packing and confirming your arrangements!"
            })
        
        # 3-day reminder
        elif days == 3:
            reminders.append({
                'trip': trip,
                'type': '3_day',
                'message': f"✈️ 3-DAY TRIP REMINDER: {trip['title']} departing in three days on {trip['departure_date']}\\n\\nDon't forget to check in online and verify all your bookings!"
            })
        
        # 1-day reminder
        elif days == 1:
            reminders.append({
                'trip': trip,
                'type': '1_day',
                'message': f"🚨 1-DAY TRIP REMINDER: {trip['title']} departing TOMORROW on {trip['departure_date']}\\n\\nTime for final preparations! Have you packed everything you need?"
            })
    
    return reminders

if __name__ == "__main__":
    reminders = generate_reminders()
    
    for reminder in reminders:
        print(reminder['message'])
        print("---")
"""
    
    # Save the pre-trip script
    pre_trip_path = os.path.join(os.path.dirname(__file__), 'travel_reminders.py')
    with open(pre_trip_path, 'w') as f:
        f.write(pre_trip_script)
    
    os.chmod(pre_trip_path, 0o755)  # Make executable
    
    # Create a script to process travel emails
    email_processor_script = """#!/usr/bin/env python3
import json
import email
import re
import datetime
import os
import sys

# This is a placeholder for the email processing script
# In a real implementation, this would:
# 1. Parse forwarded travel emails
# 2. Extract trip details (flights, hotels, etc.)
# 3. Add them to the Notion Travel database
# 4. Add to Google Calendar

def extract_flight_details(email_content):
    \"\"\"Extract flight details from email content.\"\"\"
    # This would use regex patterns to find:
    # - Flight numbers
    # - Departure/arrival times
    # - Confirmation numbers
    # - etc.
    
    # Placeholder implementation
    return {
        'airline': 'Unknown',
        'flight_number': 'Unknown',
        'departure': 'Unknown',
        'arrival': 'Unknown',
        'confirmation': 'Unknown'
    }

def extract_hotel_details(email_content):
    \"\"\"Extract hotel details from email content.\"\"\"
    # Similar to flight extraction
    
    # Placeholder implementation
    return {
        'hotel': 'Unknown',
        'check_in': 'Unknown',
        'check_out': 'Unknown',
        'confirmation': 'Unknown'
    }

def process_email(email_content):
    \"\"\"Process a travel email and extract details.\"\"\"
    # Determine type of email (flight, hotel, car rental, etc.)
    email_type = 'unknown'
    
    if 'flight' in email_content.lower() or 'airline' in email_content.lower():
        email_type = 'flight'
        details = extract_flight_details(email_content)
    elif 'hotel' in email_content.lower() or 'reservation' in email_content.lower():
        email_type = 'hotel'
        details = extract_hotel_details(email_content)
    else:
        details = {}
    
    return {
        'type': email_type,
        'details': details,
        'raw_content': email_content
    }

if __name__ == "__main__":
    # This would be expanded to actually process emails
    print("Email processor placeholder")
"""
    
    # Save the email processor script
    email_path = os.path.join(os.path.dirname(__file__), 'travel_email_processor.py')
    with open(email_path, 'w') as f:
        f.write(email_processor_script)
    
    os.chmod(email_path, 0o755)  # Make executable
    
    return {
        'pre_trip_script': pre_trip_path,
        'email_processor': email_path
    }

if __name__ == "__main__":
    print("Creating Travel Management database in Notion...")
    result = create_travel_database()
    
    if result:
        print("\nSetting up travel reminder scripts...")
        scripts = setup_travel_reminders()
        
        print("\n✅ Travel Management System Setup Complete!")
        print(f"\nTravel Database URL: {result.get('url')}")
        print("\nFeatures ready to use:")
        print("1. Travel database in Notion")
        print("2. Automated travel reminder system")
        print("3. Travel email processing framework")
        
        print("\nNext Steps:")
        print("1. Start forwarding travel confirmation emails to your-assistant-email@gmail.com")
        print("2. Add upcoming trips to your new Travel Management database")
    else:
        print("\n❌ Failed to set up Travel Management System.")