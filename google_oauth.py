#!/usr/bin/env python3
import os
import json
import pickle
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define scopes - we need Gmail and Calendar access
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

def create_oauth_url():
    """Generate an OAuth URL for authorization."""
    # Load client secrets from file
    client_secrets_file = 'client_secret.json'
    if not os.path.exists(client_secrets_file):
        print(f"Error: {client_secrets_file} not found.")
        sys.exit(1)
        
    # Create flow instance using client secrets file
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES)
    
    # Generate URL for authorization
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )
    
    print("\nAuthorization URL:")
    print(auth_url)
    print("\nPlease visit this URL to authorize access to your Google account.")
    print("After approval, copy the entire redirect URL and provide it to me.")
    
    return flow

def exchange_code(flow, redirect_url):
    """Exchange authorization code for tokens."""
    # Extract code from redirect URL
    try:
        code = redirect_url.split('code=')[1].split('&')[0]
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Save credentials for future use
        with open('noah_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            
        print("\nSuccess! Credentials have been saved.")
        return creds
    except Exception as e:
        print(f"Error exchanging code: {str(e)}")
        return None

def test_credentials(creds):
    """Test if the credentials work with Gmail and Calendar APIs."""
    results = {}
    
    try:
        # Test Gmail API
        gmail_service = build('gmail', 'v1', credentials=creds)
        profile = gmail_service.users().getProfile(userId='me').execute()
        results['gmail'] = f"Success! Connected to Gmail as: {profile['emailAddress']}"
    except Exception as e:
        results['gmail'] = f"Error with Gmail API: {str(e)}"
    
    try:
        # Test Calendar API
        cal_service = build('calendar', 'v3', credentials=creds)
        calendars = cal_service.calendarList().list().execute()
        cal_count = len(calendars.get('items', []))
        results['calendar'] = f"Success! Connected to Calendar API. Found {cal_count} calendars."
    except Exception as e:
        results['calendar'] = f"Error with Calendar API: {str(e)}"
    
    return results

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments, generate OAuth URL
        flow = create_oauth_url()
        
    elif len(sys.argv) == 2 and sys.argv[1].startswith('http'):
        # Received redirect URL, exchange code for token
        # First recreate the flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        redirect_url = sys.argv[1]
        creds = exchange_code(flow, redirect_url)
        
        if creds:
            # Test the credentials
            results = test_credentials(creds)
            for api, status in results.items():
                print(f"\n{api.upper()}: {status}")
    else:
        print("Usage: python google_oauth.py [redirect_url]")
        print("Run without arguments to generate the OAuth URL.")
        print("Run with the redirect URL to exchange the authorization code for tokens.")