#!/usr/bin/env python3
import json
import urllib.parse
import urllib.request
import sys
import base64
import os

def parse_url(redirect_url):
    """Parse the redirect URL to extract the authorization code."""
    parsed = urllib.parse.urlparse(redirect_url)
    params = urllib.parse.parse_qs(parsed.query)
    return params.get('code', [''])[0]

def exchange_code(code):
    """Exchange authorization code for tokens."""
    # Load client secrets
    with open('client_secret.json', 'r') as f:
        client_secrets = json.load(f)
    
    client_id = client_secrets['installed']['client_id']
    client_secret = client_secrets['installed']['client_secret']
    token_uri = client_secrets['installed']['token_uri']
    redirect_uri = 'http://localhost'
    
    # Prepare request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    data = urllib.parse.urlencode(data).encode('ascii')
    
    # Make request to exchange code for tokens
    req = urllib.request.Request(token_uri, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            tokens = json.loads(response.read().decode('utf-8'))
            
        # Save tokens to file
        with open('google_tokens.json', 'w') as f:
            json.dump(tokens, f)
            
        print("Success! Tokens have been exchanged and saved.")
        return tokens
    except Exception as e:
        print(f"Error exchanging code for tokens: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python exchange_token.py <redirect_url>")
        sys.exit(1)
        
    redirect_url = sys.argv[1]
    code = parse_url(redirect_url)
    
    if not code:
        print("Error: Could not extract authorization code from the URL.")
        sys.exit(1)
        
    print(f"Extracted code: {code[:10]}...")
    tokens = exchange_code(code)