#!/usr/bin/env python3
import json
import urllib.request
import urllib.parse
import datetime
import base64
import email.mime.text
import email.mime.multipart
from email.mime.text import MIMEText

def refresh_token_if_needed():
    """Check if access token is expired and refresh if needed."""
    with open('google_tokens.json', 'r') as f:
        tokens = json.load(f)
        
    # For simplicity, we'll refresh the token if it exists
    # In a production environment, you'd check expiration time
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
    
def test_gmail_api():
    """Test Gmail API access."""
    tokens = refresh_token_if_needed()
    
    # Prepare API request headers
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # Get user profile
    url = "https://gmail.googleapis.com/gmail/v1/users/me/profile"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            profile = json.loads(response.read().decode('utf-8'))
        print(f"Gmail API: Successfully accessed account {profile.get('emailAddress')}")
        return True
    except Exception as e:
        print(f"Gmail API: Error accessing profile: {str(e)}")
        return False
        
def test_calendar_api():
    """Test Calendar API access."""
    tokens = refresh_token_if_needed()
    
    # Prepare API request headers
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # List calendars
    url = "https://www.googleapis.com/calendar/v3/users/me/calendarList"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            calendars = json.loads(response.read().decode('utf-8'))
            
        cal_count = len(calendars.get('items', []))
        print(f"Calendar API: Successfully accessed {cal_count} calendars")
        
        # Print calendar names
        print("Available calendars:")
        for cal in calendars.get('items', []):
            print(f"- {cal.get('summary')} ({cal.get('id')})")
            
        return True
    except Exception as e:
        print(f"Calendar API: Error listing calendars: {str(e)}")
        return False

def send_test_email():
    """Send a test email."""
    tokens = refresh_token_if_needed()
    
    # Create message
    message = email.mime.multipart.MIMEMultipart()
    message['to'] = "your-personal-email@gmail.com"
    message['from'] = "your-assistant-email@gmail.com"
    message['subject'] = "Test Email from Noah"
    
    text = """
    Hello Simon,
    
    This is a test email to verify that the Gmail API integration is working correctly.
    
    Best,
    Noah
    """
    
    msg = email.mime.text.MIMEText(text)
    message.attach(msg)
    
    # Encode message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    # Prepare API request headers
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # Send email
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
    body = json.dumps({"raw": encoded_message}).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        print(f"Email sent successfully. Message ID: {result.get('id')}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def create_test_calendar_event():
    """Create a test calendar event."""
    tokens = refresh_token_if_needed()
    
    # Calculate event time (tomorrow at 3 PM UTC)
    now = datetime.datetime.utcnow()
    tomorrow = now + datetime.timedelta(days=1)
    start_time = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 15, 0, 0)
    end_time = start_time + datetime.timedelta(minutes=30)
    
    # Format times for Google Calendar API
    start_str = start_time.isoformat() + 'Z'
    end_str = end_time.isoformat() + 'Z'
    
    # Create event data
    event = {
        'summary': 'Test Calendar Event - Noah Setup Successful',
        'location': 'Virtual',
        'description': 'This is a test event to confirm that Noah can manage your calendar.',
        'start': {
            'dateTime': start_str,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_str,
            'timeZone': 'UTC',
        },
        'attendees': [
            {'email': 'your-company-a-email@example.com'}
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 15},
                {'method': 'popup', 'minutes': 10},
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
    # Run tests
    print("\n=== Testing Gmail API ===")
    test_gmail_api()
    
    print("\n=== Testing Calendar API ===")
    test_calendar_api()
    
    print("\n=== Sending Test Email ===")
    send_test_email()
    
    print("\n=== Creating Test Calendar Event ===")
    create_test_calendar_event()