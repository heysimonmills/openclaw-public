#!/usr/bin/env python3
import json
import urllib.request
import base64
import email.mime.text
import email.mime.multipart
from email.mime.text import MIMEText

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
    
def send_email_to_ian():
    """Send an introduction email to Ian."""
    tokens = refresh_token_if_needed()
    
    # Create message
    message = email.mime.multipart.MIMEMultipart()
    message['to'] = "contact@example.com"
    message['from'] = "Noah <your-assistant-email@gmail.com>"
    message['subject'] = "Hello from Noah (Simon's Calendar Assistant)"
    
    text = """
Hi Ian,

I'm Noah, Simon's new AI assistant. Simon asked me to reach out and introduce myself to you. I'll be helping Simon manage his calendar, schedule meetings, and keep track of important events.

Simon has set me up with access to his calendars so I can help coordinate his schedule more efficiently. I'm still getting to know Simon's routines and preferences, but I'm looking forward to making his life a bit more organized.

If you ever need to coordinate anything with Simon or check his availability, feel free to mention it to him and I can help arrange things.

Nice to "meet" you!

Best regards,
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
        print(f"Email sent successfully to Ian. Message ID: {result.get('id')}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    send_email_to_ian()