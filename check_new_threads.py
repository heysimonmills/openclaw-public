#!/usr/bin/env python3
import json
import urllib.request
import urllib.parse
import os

def refresh_token_if_needed():
    """Check if access token is expired and refresh if needed."""
    with open('google_tokens.json', 'r') as f:
        tokens = json.load(f)
        
    if 'refresh_token' in tokens:
        with open('client_secret.json', 'r') as f:
            client_secrets = json.load(f)
        
        client_id = client_secrets['installed']['client_id']
        client_secret = client_secrets['installed']['client_secret']
        token_uri = client_secrets['installed']['token_uri']
        
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
        req = urllib.request.Request(token_uri, data=data, headers=headers)
        
        try:
            with urllib.request.urlopen(req) as response:
                new_tokens = json.loads(response.read().decode('utf-8'))
                
            if 'refresh_token' not in new_tokens and 'refresh_token' in tokens:
                new_tokens['refresh_token'] = tokens['refresh_token']
                
            with open('google_tokens.json', 'w') as f:
                json.dump(new_tokens, f)
                
            return new_tokens
        except Exception as e:
            print(f"Error refreshing token: {str(e)}")
            return tokens
    return tokens

def get_tracked_threads():
    """Read tracked thread IDs from email-tracking.md"""
    tracked_threads = set()
    try:
        with open('memory/email-tracking.md', 'r') as f:
            for line in f:
                if '|' in line and not line.startswith('#') and 'YYYY-MM-DD' not in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        thread_id = parts[1].strip()
                        if thread_id and thread_id != 'Thread ID':
                            tracked_threads.add(thread_id)
    except FileNotFoundError:
        print("email-tracking.md not found, treating all emails as new")
    
    return tracked_threads

def check_new_emails():
    """Check for new emails by thread ID."""
    tokens = refresh_token_if_needed()
    tracked_threads = get_tracked_threads()
    
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # Get recent emails (last 3 days)
    query = "newer_than:3d"
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={urllib.parse.quote(query)}&maxResults=30"
    
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error listing emails: {str(e)}")
        return []
    
    messages = result.get('messages', [])
    if not messages:
        print("No emails found in the last 3 days")
        return []
    
    # Get details for each message
    new_emails = []
    for msg in messages:
        msg_id = msg['id']
        thread_id = msg['threadId']
        
        # Skip if we've already tracked this thread
        if thread_id in tracked_threads:
            continue
        
        # Fetch full message details
        msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date"
        msg_req = urllib.request.Request(msg_url, headers=headers)
        
        try:
            with urllib.request.urlopen(msg_req) as response:
                full_msg = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Error fetching message {msg_id}: {str(e)}")
            continue
        
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
        
        new_emails.append({
            'id': msg_id,
            'threadId': thread_id,
            'subject': subject,
            'from': from_email,
            'date': date
        })
    
    return new_emails

if __name__ == "__main__":
    new_emails = check_new_emails()
    
    if new_emails:
        print(json.dumps(new_emails, indent=2))
    else:
        print("[]")
