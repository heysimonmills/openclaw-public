#!/usr/bin/env python3
import json
import urllib.parse
import sys

# Load client secrets from file
try:
    with open('client_secret.json', 'r') as f:
        client_secrets = json.load(f)
        
    # Extract client ID and other details
    client_id = client_secrets['installed']['client_id']
    auth_uri = client_secrets['installed']['auth_uri']
    redirect_uri = 'http://localhost'
    
    # Define scopes - we need Gmail and Calendar access
    scopes = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify', 
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    # Build authorization URL
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': ' '.join(scopes),
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
        'include_granted_scopes': 'true'
    }
    
    auth_url = f"{auth_uri}?{urllib.parse.urlencode(params)}"
    
    print("\nAuthorization URL:")
    print(auth_url)
    print("\nPlease visit this URL to authorize access to your Google account.")
    print("After approval, copy the entire redirect URL and provide it.")
    
except Exception as e:
    print(f"Error: {str(e)}")