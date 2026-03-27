#!/usr/bin/env python3
import json
import urllib.request
import datetime
import os
import sys
import time

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

def get_calendar_timestamp():
    """Get the timestamp of the last checked calendar."""
    timestamp_file = 'last_calendar_check.txt'
    if os.path.exists(timestamp_file):
        with open(timestamp_file, 'r') as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def save_calendar_timestamp(timestamp):
    """Save the timestamp of the last checked calendar."""
    timestamp_file = 'last_calendar_check.txt'
    with open(timestamp_file, 'w') as f:
        f.write(str(timestamp))

def check_upcoming_events():
    """Check for upcoming events in the next 24 hours."""
    tokens = refresh_token_if_needed()
    
    # Get the current time and time 24 hours from now
    now = datetime.datetime.now(datetime.timezone.utc)
    day_later = now + datetime.timedelta(hours=24)
    
    # Format times for Google Calendar API
    time_min = now.isoformat()
    time_max = day_later.isoformat()
    
    # Get the last check timestamp
    last_check = get_calendar_timestamp()
    current_time = int(time.time())
    
    # Prepare API request headers
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # Get list of calendars
    calendars_url = "https://www.googleapis.com/calendar/v3/users/me/calendarList"
    cal_req = urllib.request.Request(calendars_url, headers=headers)
    
    try:
        all_events = []
        
        with urllib.request.urlopen(cal_req) as response:
            calendars = json.loads(response.read().decode('utf-8'))
        
        # For each calendar, get upcoming events
        for calendar in calendars.get('items', []):
            cal_id = calendar['id']
            cal_name = calendar.get('summary', 'Unnamed Calendar')
            
            # List events
            events_url = f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(cal_id)}/events"
            events_url += f"?timeMin={urllib.parse.quote(time_min)}&timeMax={urllib.parse.quote(time_max)}"
            events_url += "&singleEvents=true&orderBy=startTime"
            
            events_req = urllib.request.Request(events_url, headers=headers)
            with urllib.request.urlopen(events_req) as response:
                events_data = json.loads(response.read().decode('utf-8'))
                
            for event in events_data.get('items', []):
                # Extract event details
                start = event.get('start', {})
                end = event.get('end', {})
                
                # Convert to datetime objects
                start_time = None
                if 'dateTime' in start:
                    start_time = datetime.datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                elif 'date' in start:
                    start_time = datetime.datetime.fromisoformat(start['date'])
                
                if not start_time:
                    continue
                
                # Only include events in the next 24 hours
                if start_time > day_later:
                    continue
                
                # Check if this is a new/updated event since last check
                updated = datetime.datetime.fromisoformat(event.get('updated', '').replace('Z', '+00:00'))
                updated_timestamp = int(updated.timestamp())
                
                # Include event if it's new since the last check, or it starts within the next 2 hours
                hours_until_event = (start_time - now).total_seconds() / 3600
                
                if updated_timestamp > last_check or hours_until_event <= 2:
                    all_events.append({
                        'id': event.get('id', ''),
                        'summary': event.get('summary', 'No Title'),
                        'location': event.get('location', 'No Location'),
                        'start': start,
                        'end': end,
                        'calendar': cal_name,
                        'link': event.get('htmlLink', ''),
                        'hours_until': hours_until_event
                    })
        
        # Update the timestamp
        save_calendar_timestamp(current_time)
        
        # Sort events by start time
        all_events.sort(key=lambda x: x.get('hours_until', 0))
        
        return all_events
    except Exception as e:
        print(f"Error checking calendar: {str(e)}")
        return []

if __name__ == "__main__":
    events = check_upcoming_events()
    
    if events:
        print(f"Found {len(events)} upcoming event(s):")
        for i, event in enumerate(events, 1):
            start_info = event.get('start', {})
            start_str = start_info.get('dateTime', start_info.get('date', 'Unknown'))
            
            print(f"\n=== Event {i} ===")
            print(f"Calendar: {event['calendar']}")
            print(f"Title: {event['summary']}")
            print(f"When: {start_str}")
            print(f"Where: {event['location']}")
            print(f"Hours until: {event['hours_until']:.1f}")
            print(f"Link: {event['link']}")
            print("="*50)
    else:
        print("No upcoming events found in the next 24 hours.")