#!/usr/bin/env python3
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def check_gmail():
    token_file = '/home/ubuntu/clawd/google_tokens.json'
    
    # Load credentials
    with open(token_file, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data.get('access_token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id='',  # Will use defaults
        client_secret='',
        scopes=token_data.get('scope', '').split()
    )
    
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token
            token_data['access_token'] = creds.token
            with open(token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
    
    # Build Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    
    # Get list of messages
    results = service.users().messages().list(
        userId='me',
        maxResults=20,
        labelIds=['INBOX']
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("No messages found.")
        return
    
    # Get details for each message
    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['Subject', 'From', 'Date']
        ).execute()
        
        thread_id = msg_data.get('threadId', '')
        headers = msg_data.get('payload', {}).get('headers', [])
        
        subject = ''
        from_addr = ''
        date = ''
        
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            elif header['name'] == 'From':
                from_addr = header['value']
            elif header['name'] == 'Date':
                date = header['value']
        
        print(f"ThreadID: {thread_id}")
        print(f"Subject: {subject}")
        print(f"From: {from_addr}")
        print(f"Date: {date}")
        print("---")

if __name__ == '__main__':
    check_gmail()
