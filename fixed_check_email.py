#!/usr/bin/env python3
import json
import urllib.request
import base64
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

def get_email_timestamp():
    """Get the timestamp of the last checked email."""
    timestamp_file = 'last_email_check.txt'
    if os.path.exists(timestamp_file):
        with open(timestamp_file, 'r') as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def save_email_timestamp(timestamp):
    """Save the timestamp of the last checked email."""
    timestamp_file = 'last_email_check.txt'
    with open(timestamp_file, 'w') as f:
        f.write(str(timestamp))

def check_new_emails():
    """Check for new emails since the last check."""
    tokens = refresh_token_if_needed()
    
    # Get the last check timestamp
    last_check = get_email_timestamp()
    current_time = int(time.time())
    
    # Prepare API request headers
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # Build query for emails received after the last check
    # For simplicity, just check for unread emails
    query = "is:unread"
    
    # List emails
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        messages = result.get('messages', [])
        if not messages:
            print("No new emails found.")
            save_email_timestamp(current_time)
            return []
            
        # Get details for each message
        new_emails = []
        for msg in messages[:5]:  # Limit to 5 newest emails
            msg_id = msg['id']
            msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}"
            msg_req = urllib.request.Request(msg_url, headers=headers)
            with urllib.request.urlopen(msg_req) as response:
                full_msg = json.loads(response.read().decode('utf-8'))
                
            # Extract email details
            headers_list = full_msg.get('payload', {}).get('headers', [])
            subject = "No Subject"
            from_email = "Unknown Sender"
            date = "Unknown Date"
            
            for header in headers_list:
                name = header.get('name', '').lower()
                if name == 'subject':
                    subject = header.get('value', 'No Subject')
                elif name == 'from':
                    from_email = header.get('value', 'Unknown Sender')
                elif name == 'date':
                    date = header.get('value', 'Unknown Date')
            
            # Extract body
            body = ""
            payload = full_msg.get('payload', {})
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        body_data = part.get('body', {}).get('data', '')
                        if body_data:
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                            break
            elif 'body' in payload and 'data' in payload['body']:
                body_data = payload['body']['data']
                body = base64.urlsafe_b64decode(body_data).decode('utf-8')
            
            new_emails.append({
                'id': msg_id,
                'subject': subject,
                'from': from_email,
                'date': date,
                'body': body[:1000] + ('...' if len(body) > 1000 else '')  # Truncate long bodies
            })
        
        # Update the timestamp
        save_email_timestamp(current_time)
        
        return new_emails
    except Exception as e:
        print(f"Error checking emails: {str(e)}")
        return []

if __name__ == "__main__":
    new_emails = check_new_emails()
    
    if new_emails:
        print(f"Found {len(new_emails)} new email(s):")
        for i, email in enumerate(new_emails, 1):
            print(f"\n=== Email {i} ===")
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            print(f"Date: {email['date']}")
            print(f"\nBody:\n{email['body']}")
            print("="*50)
    else:
        print("No new emails found.")