#!/usr/bin/env python3
import json
import urllib.request
import urllib.parse
import os

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

def check_emails():
    """Check for new emails."""
    tokens = refresh_token_if_needed()
    
    # Prepare API request headers
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # List emails from the last 3 days (to catch anything recent)
    query = "newer_than:3d"
    
    # List emails
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={urllib.parse.quote(query)}&maxResults=50"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        messages = result.get('messages', [])
        if not messages:
            print(json.dumps([]))
            return
            
        # Get thread IDs only (faster)
        emails = []
        for msg in messages[:50]:
            msg_id = msg['id']
            thread_id = msg['threadId']
            
            msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date"
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
            
            emails.append({
                'threadId': thread_id,
                'subject': subject,
                'from': from_email,
                'date': date
            })
        
        print(json.dumps(emails, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}", file=os.sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_emails()
