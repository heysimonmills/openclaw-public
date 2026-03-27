#!/usr/bin/env python3
import json
import urllib.request
import datetime
from datetime import timezone, timedelta

def refresh_token_if_needed():
    """Check if access token is expired and refresh if needed."""
    with open('google_tokens.json', 'r') as f:
        tokens = json.load(f)
        
    # For simplicity, we'll refresh the token if it exists
    if 'refresh_token' in tokens:
        # Load client secrets
        with open('client_secret.json', 'r') as f:
            client_secrets = json.load(f)
        
        client_id = client_secrets['installed']['client_id']
        client_secret = client_secrets['installed']['client_secret']
        token_uri = client_secrets['installed']['token_uri']
        
        # Prepare request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': tokens['refresh_token'],
            'grant_type': 'refresh_token'
        }
        
        data = urllib.parse.urlencode(data).encode('ascii')
        
        # Make request to refresh token
        req = urllib.request.Request(token_uri, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                new_tokens = json.loads(response.read().decode('utf-8'))
                
            # Preserve the refresh token if not returned in the response
            if 'refresh_token' not in new_tokens and 'refresh_token' in tokens:
                new_tokens['refresh_token'] = tokens['refresh_token']
                
            # Save updated tokens
            with open('google_tokens.json', 'w') as f:
                json.dump(new_tokens, f)
                
            return new_tokens
        except Exception as e:
            print(f"Error refreshing token: {str(e)}")
            return tokens
    return tokens

def create_calendar_event(summary, start_date, end_date, description="", location=""):
    """Create a calendar event."""
    tokens = refresh_token_if_needed()
    
    # Prepare event data
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'date': start_date,
            'timeZone': 'America/Toronto',
        },
        'end': {
            'date': end_date,
            'timeZone': 'America/Toronto',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                {'method': 'popup', 'minutes': 24 * 60},  # 1 day before
            ],
        }
    }
    
    # Add location if provided
    if location:
        event['location'] = location
    
    # Prepare API request headers
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # Create event
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    body = json.dumps(event).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        print(f"Created event: {summary}")
        print(f"ID: {result.get('id')}")
        print(f"Link: {result.get('htmlLink')}")
        return True, result
    except Exception as e:
        print(f"Error creating event: {str(e)}")
        return False, str(e)

# Create all the travel events
def create_travel_events():
    """Create all travel events from the forwarded emails."""
    events = [
        {
            'summary': 'Airbnb Stay: February 14-21, 2026',
            'start_date': '2026-02-14',
            'end_date': '2026-02-21',
            'description': 'Airbnb booking for February 14-21, 2026.',
            'location': ''
        },
        {
            'summary': 'Airbnb Stay: March 8-15, 2026',
            'start_date': '2026-03-08',
            'end_date': '2026-03-15',
            'description': 'Airbnb booking for March 8-15, 2026.',
            'location': 'Mexico City'
        },
        {
            'summary': 'Flight: Toronto to Mexico City',
            'start_date': '2026-03-08',
            'end_date': '2026-03-08',
            'description': 'Air Canada flight to Mexico City\nBooking Reference: A8Q8Q6',
            'location': 'Toronto Pearson International Airport'
        },
        {
            'summary': 'Gianni Visit to Toronto',
            'start_date': '2026-06-06',
            'end_date': '2026-06-06',
            'description': 'Gianni Jasper Dazo visiting Toronto\nBooking Reference: ACJOLN',
            'location': 'Toronto'
        }
    ]
    
    results = []
    for event in events:
        success, result = create_calendar_event(
            event['summary'],
            event['start_date'],
            event['end_date'],
            event['description'],
            event['location']
        )
        results.append({
            'success': success,
            'event': event['summary'],
            'result': result
        })
        print('-' * 40)
    
    return results

if __name__ == "__main__":
    print("Adding travel events to calendar...")
    results = create_travel_events()
    
    success_count = sum(1 for r in results if r['success'])
    print(f"\nSuccessfully added {success_count} of {len(results)} events to calendar.")