#!/usr/bin/env python3
import datetime
import pickle
import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Calculate event time (tomorrow at 3 PM UTC)
    now = datetime.datetime.utcnow()
    tomorrow = now + datetime.timedelta(days=1)
    start_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 15, 0, 0)
    end_time = start_time + datetime.timedelta(minutes=30)
    
    # Format times for Google Calendar API
    start_str = start_time.isoformat() + 'Z'
    end_str = end_time.isoformat() + 'Z'

    # Create the event
    event = {
        'summary': 'Test Calendar Event - Noah Setup Successful',
        'location': 'Virtual',
        'description': 'This is a test event to confirm that Noah can manage your calendar. If you see this event, the setup was successful!',
        'start': {
            'dateTime': start_str,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_str,
            'timeZone': 'UTC',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 15},
            ],
        },
    }

    # Insert the event - use 'primary' for the user's primary calendar
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")

if __name__ == '__main__':
    main()