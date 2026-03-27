#!/usr/bin/env python3
"""
Matter API integration - Add URLs to read-later queue
Usage: python3 matter_api.py add <url>
"""
import json
import requests
import sys
import os

# Matter API config
MATTER_API_BASE = "https://api.getmatter.app/api/v11"

# Token should be stored in config file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'matter_config.json')

def load_token():
    """Load Matter API token from config."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            return config.get('token')
    return None

def save_token(token):
    """Save Matter API token to config."""
    config = {'token': token}
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Token saved to {CONFIG_PATH}")

def add_to_matter(url, token=None):
    """Add a URL to Matter queue."""
    if not token:
        token = load_token()
    
    if not token:
        return {
            'success': False,
            'error': 'No Matter API token found. Please set it up first.'
        }
    
    api_url = f"{MATTER_API_BASE}/save/"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'url': url
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            return {
                'success': True,
                'message': f"Added to Matter: {url}"
            }
        elif response.status_code == 401:
            return {
                'success': False,
                'error': 'Invalid or expired token. Please re-authenticate.'
            }
        else:
            return {
                'success': False,
                'error': f'API error: {response.status_code} - {response.text}'
            }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': 'Request timed out. Please try again.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error: {str(e)}'
        }

def test_connection(token=None):
    """Test if token is valid."""
    if not token:
        token = load_token()
    
    if not token:
        return {'valid': False, 'error': 'No token found'}
    
    # Try to fetch highlights feed as a test
    api_url = f"{MATTER_API_BASE}/library_items/highlights_feed"
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return {'valid': True}
        else:
            return {'valid': False, 'error': f'Status {response.status_code}'}
    except Exception as e:
        return {'valid': False, 'error': str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 matter_api.py add <url>     - Add URL to Matter")
        print("  python3 matter_api.py setup <token> - Save API token")
        print("  python3 matter_api.py test          - Test connection")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "add" and len(sys.argv) > 2:
        url = sys.argv[2]
        result = add_to_matter(url)
        if result['success']:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    elif command == "setup" and len(sys.argv) > 2:
        token = sys.argv[2]
        save_token(token)
        # Test it
        test_result = test_connection(token)
        if test_result['valid']:
            print("✅ Token is valid and working!")
        else:
            print(f"⚠️ Warning: Token test failed - {test_result.get('error', 'unknown error')}")
    
    elif command == "test":
        result = test_connection()
        if result['valid']:
            print("✅ Matter connection is working!")
        else:
            print(f"❌ Connection failed: {result.get('error', 'unknown error')}")
    
    else:
        print("Unknown command. Use: add, setup, or test")
