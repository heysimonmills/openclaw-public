#!/usr/bin/env python3
import json
import urllib.request
import datetime
import os
import sys
from datetime import datetime, timedelta, timezone
import re

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

def check_calendar_availability(date_str, start_time_str, end_time_str):
    """Check if a time slot is available on the calendar."""
    tokens = refresh_token_if_needed()
    
    # Parse the date and times
    try:
        # Create datetime objects in Toronto time zone (UTC-5)
        tz_offset = timedelta(hours=-5)  # EST timezone offset
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Convert time strings (e.g., "9:00") to datetime objects
        start_time_parts = [int(x) for x in start_time_str.split(':')]
        end_time_parts = [int(x) for x in end_time_str.split(':')]
        
        # Create full datetime objects
        start_datetime = datetime(
            date_obj.year, date_obj.month, date_obj.day,
            start_time_parts[0], start_time_parts[1], 0,
            tzinfo=timezone(tz_offset)
        )
        
        end_datetime = datetime(
            date_obj.year, date_obj.month, date_obj.day,
            end_time_parts[0], end_time_parts[1], 0,
            tzinfo=timezone(tz_offset)
        )
        
        # Convert to ISO format for API
        start_str = start_datetime.isoformat()
        end_str = end_datetime.isoformat()
    except Exception as e:
        return False, f"Error parsing date/time: {str(e)}"
    
    # Prepare API request headers
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # Get list of calendars
    calendars_url = "https://www.googleapis.com/calendar/v3/users/me/calendarList"
    cal_req = urllib.request.Request(calendars_url, headers=headers)
    
    try:
        # Get all calendars
        with urllib.request.urlopen(cal_req) as response:
            calendars = json.loads(response.read().decode('utf-8'))
        
        # Check each calendar for conflicts
        for calendar in calendars.get('items', []):
            cal_id = calendar['id']
            
            # Query for events in this time range
            events_url = f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(cal_id)}/events"
            events_url += f"?timeMin={urllib.parse.quote(start_str)}&timeMax={urllib.parse.quote(end_str)}"
            events_url += "&singleEvents=true"
            
            events_req = urllib.request.Request(events_url, headers=headers)
            with urllib.request.urlopen(events_req) as response:
                events_data = json.loads(response.read().decode('utf-8'))
            
            # If any events exist in this time slot, it's not available
            if events_data.get('items', []):
                event_titles = [e.get('summary', 'Untitled Event') for e in events_data.get('items', [])]
                return False, f"Conflict with: {', '.join(event_titles)}"
        
        # If we got here, no conflicts were found
        return True, "Time slot available"
    except Exception as e:
        return False, f"Error checking calendar: {str(e)}"

def create_calendar_event(summary, date_str, start_time_str, end_time_str, description=None, location=None):
    """Create a calendar event."""
    tokens = refresh_token_if_needed()
    
    # Parse the date and times
    try:
        # Create datetime objects in Toronto time zone (UTC-5)
        tz_offset = timedelta(hours=-5)  # EST timezone offset
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Convert time strings (e.g., "9:00") to datetime objects
        start_time_parts = [int(x) for x in start_time_str.split(':')]
        end_time_parts = [int(x) for x in end_time_str.split(':')]
        
        # Create full datetime objects
        start_datetime = datetime(
            date_obj.year, date_obj.month, date_obj.day,
            start_time_parts[0], start_time_parts[1], 0,
            tzinfo=timezone(tz_offset)
        )
        
        end_datetime = datetime(
            date_obj.year, date_obj.month, date_obj.day,
            end_time_parts[0], end_time_parts[1], 0,
            tzinfo=timezone(tz_offset)
        )
        
        # Convert to ISO format for API
        start_str = start_datetime.isoformat()
        end_str = end_datetime.isoformat()
    except Exception as e:
        return False, f"Error parsing date/time: {str(e)}"
    
    # Create event data
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_str,
            'timeZone': 'America/Toronto',
        },
        'end': {
            'dateTime': end_str,
            'timeZone': 'America/Toronto',
        },
        'reminders': {
            'useDefault': True
        }
    }
    
    # Add optional fields if provided
    if description:
        event['description'] = description
    
    if location:
        event['location'] = location
    
    # Prepare API request headers
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # Create event in the primary calendar
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    body = json.dumps(event).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        return True, {
            'id': result.get('id'),
            'link': result.get('htmlLink'),
            'summary': summary,
            'start': start_time_str,
            'end': end_time_str,
            'date': date_str
        }
    except Exception as e:
        return False, f"Error creating event: {str(e)}"

def find_free_slots(date_str, duration_minutes=60, start_hour=9, end_hour=17, min_slot_minutes=30):
    """Find free time slots on the given date."""
    tokens = refresh_token_if_needed()
    
    # Parse the date
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Create datetime objects in Toronto time zone (UTC-5)
        tz_offset = timedelta(hours=-5)  # EST timezone offset
        
        # Start and end of the work day
        day_start = datetime(
            date_obj.year, date_obj.month, date_obj.day,
            start_hour, 0, 0,
            tzinfo=timezone(tz_offset)
        )
        
        day_end = datetime(
            date_obj.year, date_obj.month, date_obj.day,
            end_hour, 0, 0,
            tzinfo=timezone(tz_offset)
        )
        
        # Convert to ISO format for API
        day_start_str = day_start.isoformat()
        day_end_str = day_end.isoformat()
    except Exception as e:
        return False, f"Error parsing date: {str(e)}"
    
    # Prepare API request headers
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # Get list of calendars
    calendars_url = "https://www.googleapis.com/calendar/v3/users/me/calendarList"
    cal_req = urllib.request.Request(calendars_url, headers=headers)
    
    try:
        # Get all calendars and their events
        all_events = []
        
        with urllib.request.urlopen(cal_req) as response:
            calendars = json.loads(response.read().decode('utf-8'))
        
        # Get events from each calendar
        for calendar in calendars.get('items', []):
            cal_id = calendar['id']
            
            # Query for events on this day
            events_url = f"https://www.googleapis.com/calendar/v3/calendars/{urllib.parse.quote(cal_id)}/events"
            events_url += f"?timeMin={urllib.parse.quote(day_start_str)}&timeMax={urllib.parse.quote(day_end_str)}"
            events_url += "&singleEvents=true&orderBy=startTime"
            
            events_req = urllib.request.Request(events_url, headers=headers)
            with urllib.request.urlopen(events_req) as response:
                events_data = json.loads(response.read().decode('utf-8'))
            
            # Add events to our list
            for event in events_data.get('items', []):
                # Only consider events with start and end times
                start = event.get('start', {}).get('dateTime')
                end = event.get('end', {}).get('dateTime')
                
                if start and end:
                    all_events.append({
                        'summary': event.get('summary', 'Untitled Event'),
                        'start': start,
                        'end': end
                    })
        
        # Sort events by start time
        all_events.sort(key=lambda x: x['start'])
        
        # Find free slots
        free_slots = []
        current_time = day_start
        
        # Check each event to find gaps
        for event in all_events:
            event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
            event_end = datetime.fromisoformat(event['end'].replace('Z', '+00:00'))
            
            # If there's a gap before this event, check if it's big enough
            if event_start > current_time:
                gap_minutes = (event_start - current_time).total_seconds() / 60
                
                # If the gap is big enough for the requested duration
                if gap_minutes >= duration_minutes:
                    free_slots.append({
                        'start': current_time.strftime('%H:%M'),
                        'end': event_start.strftime('%H:%M'),
                        'duration_minutes': gap_minutes
                    })
                    
            # Move current_time to after this event
            current_time = max(current_time, event_end)
        
        # Check if there's time left at the end of the day
        if current_time < day_end:
            gap_minutes = (day_end - current_time).total_seconds() / 60
            
            if gap_minutes >= duration_minutes:
                free_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': day_end.strftime('%H:%M'),
                    'duration_minutes': gap_minutes
                })
        
        # Return the free slots
        return True, free_slots
    except Exception as e:
        return False, f"Error finding free slots: {str(e)}"

def suggest_calendar_blocks(date_str, tasks, default_duration_minutes=30):
    """Suggest calendar blocks for a list of tasks."""
    success, slots_or_error = find_free_slots(date_str)
    
    if not success:
        return False, slots_or_error
    
    free_slots = slots_or_error
    
    if not free_slots:
        return False, "No free time slots available on this day."
    
    # Match tasks to free slots
    suggestions = []
    slot_index = 0
    
    for task in tasks:
        # Skip if we're out of slots
        if slot_index >= len(free_slots):
            suggestions.append({
                'task': task,
                'status': 'No available time slot'
            })
            continue
        
        # Get the current slot
        slot = free_slots[slot_index]
        
        # Calculate end time
        start_time = datetime.strptime(slot['start'], '%H:%M')
        end_time = start_time + timedelta(minutes=default_duration_minutes)
        end_time_str = end_time.strftime('%H:%M')
        
        # Check if the end time fits within the slot
        slot_end = datetime.strptime(slot['end'], '%H:%M')
        
        if end_time <= slot_end:
            # This task fits in the current slot
            suggestions.append({
                'task': task,
                'status': 'Suggested',
                'start': slot['start'],
                'end': end_time_str,
                'date': date_str
            })
            
            # Update the slot's start time
            new_start = end_time.strftime('%H:%M')
            free_slots[slot_index]['start'] = new_start
            
            # Update remaining duration
            free_slots[slot_index]['duration_minutes'] -= default_duration_minutes
            
            # If the slot is too small now, move to the next one
            if free_slots[slot_index]['duration_minutes'] < default_duration_minutes:
                slot_index += 1
        else:
            # Move to the next slot
            slot_index += 1
            
            # Try again with the next slot if available
            if slot_index < len(free_slots):
                slot = free_slots[slot_index]
                
                start_time = datetime.strptime(slot['start'], '%H:%M')
                end_time = start_time + timedelta(minutes=default_duration_minutes)
                end_time_str = end_time.strftime('%H:%M')
                
                suggestions.append({
                    'task': task,
                    'status': 'Suggested',
                    'start': slot['start'],
                    'end': end_time_str,
                    'date': date_str
                })
                
                # Update the slot's start time
                new_start = end_time.strftime('%H:%M')
                free_slots[slot_index]['start'] = new_start
                
                # Update remaining duration
                free_slots[slot_index]['duration_minutes'] -= default_duration_minutes
            else:
                # No more slots
                suggestions.append({
                    'task': task,
                    'status': 'No available time slot'
                })
    
    return True, suggestions

def process_calendar_blocking(tasks, date_str, duration_minutes=30):
    """Process a list of tasks and create calendar blocks for them."""
    # Get suggestions for calendar blocks
    success, suggestions_or_error = suggest_calendar_blocks(date_str, tasks, duration_minutes)
    
    if not success:
        return False, suggestions_or_error
    
    suggestions = suggestions_or_error
    
    # Create calendar events for the suggestions
    results = []
    
    for suggestion in suggestions:
        if suggestion['status'] == 'Suggested':
            task = suggestion['task']
            start = suggestion['start']
            end = suggestion['end']
            
            # Create the calendar event
            success, result = create_calendar_event(
                summary=f"Task: {task['name']}",
                date_str=date_str,
                start_time_str=start,
                end_time_str=end,
                description=f"Task from daily plan. Category: {task['category']}"
            )
            
            if success:
                results.append({
                    'task': task['name'],
                    'start': start,
                    'end': end,
                    'status': 'Added to calendar',
                    'link': result.get('link')
                })
            else:
                results.append({
                    'task': task['name'],
                    'status': f"Error: {result}"
                })
        else:
            results.append({
                'task': task['name'],
                'status': suggestion['status']
            })
    
    return True, results

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1 and sys.argv[1] == "create-event":
        if len(sys.argv) >= 6:
            summary = sys.argv[2]
            date_str = sys.argv[3]
            start_time = sys.argv[4]
            end_time = sys.argv[5]
            description = sys.argv[6] if len(sys.argv) > 6 else None
            
            success, result = create_calendar_event(summary, date_str, start_time, end_time, description)
            
            if success:
                print(f"Created event: {summary}")
                print(f"When: {date_str} {start_time}-{end_time}")
                print(f"Link: {result.get('link')}")
            else:
                print(f"Error: {result}")
        else:
            print("Usage: calendar_block.py create-event <summary> <date> <start_time> <end_time> [description]")
    elif len(sys.argv) > 1 and sys.argv[1] == "find-slots":
        if len(sys.argv) >= 3:
            date_str = sys.argv[2]
            duration = int(sys.argv[3]) if len(sys.argv) > 3 else 60
            
            success, result = find_free_slots(date_str, duration)
            
            if success:
                print(f"Free slots on {date_str} for {duration} minutes:")
                for i, slot in enumerate(result, 1):
                    print(f"{i}. {slot['start']}-{slot['end']} ({slot['duration_minutes']} min)")
            else:
                print(f"Error: {result}")
        else:
            print("Usage: calendar_block.py find-slots <date> [duration_minutes]")
    else:
        print("Usage:")
        print("  calendar_block.py create-event <summary> <date> <start_time> <end_time> [description]")
        print("  calendar_block.py find-slots <date> [duration_minutes]")