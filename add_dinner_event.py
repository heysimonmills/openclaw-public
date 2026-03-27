#!/usr/bin/env python3
import json
import urllib.request
import datetime
import os
import time
from datetime import timezone

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

def add_dinner_event():
    """Add a dinner event with Ian to the calendar."""
    tokens = refresh_token_if_needed()
    
    # Current time in EST (UTC-5) - Assuming Toronto time
    today = datetime.datetime.now(timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=-5))).date()
    
    # Set event to start at 7:00 PM and end at 9:00 PM
    start_time = datetime.datetime(today.year, today.month, today.day, 19, 0, 0, 
                                  tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
    end_time = datetime.datetime(today.year, today.month, today.day, 21, 0, 0,
                                tzinfo=datetime.timezone(datetime.timedelta(hours=-5)))
    
    # Format times for Google Calendar API
    start_str = start_time.isoformat()
    end_str = end_time.isoformat()
    
    # Create event data
    event = {
        'summary': 'Dinner with Ian',
        'location': 'West Queen West / Little Italy / Old Town (TBD)',
        'description': 'Dinner with Ian (Gianni). Restaurant options discussed in email: The Burger\'s Priest, Rosie\'s Burgers, The Good Son, Trattoria Nervosa, Bar Raval, Terroni, or The Carbon Bar.',
        'start': {
            'dateTime': start_str,
            'timeZone': 'America/Toronto',
        },
        'end': {
            'dateTime': end_str,
            'timeZone': 'America/Toronto',
        },
        'attendees': [
            {'email': 'your-personal-email@gmail.com'},
            {'email': 'contact@example.com'}
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 30},
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }
    
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
        print(f"Calendar event created successfully. Event ID: {result.get('id')}")
        print(f"Event link: {result.get('htmlLink')}")
        return True
    except Exception as e:
        print(f"Error creating calendar event: {str(e)}")
        return False

if __name__ == "__main__":
    add_dinner_event()