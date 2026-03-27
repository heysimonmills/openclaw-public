#!/usr/bin/env python3
"""
Clean Twitter Feed - Distraction-free timeline viewer
Fetches only tweets from people you follow, no algorithm, no ads
"""

import json
import requests
import os
from datetime import datetime
from typing import List, Dict, Optional

# Config path
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'twitter_feed_config.json')

def load_config():
    """Load Twitter API credentials."""
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def get_home_timeline(bearer_token: str, max_results: int = 50) -> List[Dict]:
    """Fetch home timeline from Twitter API v2."""
    url = "https://api.twitter.com/2/tweets/search/recent"
    
    # Note: Free tier doesn't have home_timeline endpoint
    # We'll use search/recent as workaround for mentions or fetch user tweets
    # For full home timeline, need Elevated access
    
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    
    # Get tweets from accounts you follow (requires following:ids scope)
    # Free tier workaround: Search for tweets from specific users
    
    # For now, let's get the authenticated user's timeline
    # This requires user context auth (not just bearer token)
    
    return []

def get_user_timeline(user_id: str, bearer_token: str, max_results: int = 20) -> List[Dict]:
    """Fetch a specific user's timeline."""
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    
    params = {
        "max_results": max_results,
        "tweet.fields": "created_at,author_id,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,profile_image_url"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data', [])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []

def get_auth_user(bearer_token: str) -> Optional[Dict]:
    """Get the authenticated user's info."""
    url = "https://api.twitter.com/2/users/me"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get('data')
    else:
        print(f"Error getting user: {response.status_code}")
        print(response.text)
        return None

def format_tweet(tweet: Dict, users: Dict = None) -> str:
    """Format a single tweet for display."""
    text = tweet.get('text', '')
    created_at = tweet.get('created_at', '')
    author_id = tweet.get('author_id', '')
    
    # Parse date
    if created_at:
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        time_str = dt.strftime("%b %d, %I:%M %p")
    else:
        time_str = "Unknown time"
    
    # Get username if available
    username = users.get(author_id, {}).get('username', 'Unknown') if users else 'Unknown'
    
    return f"""
@{username} · {time_str}
{text}
---"""

def fetch_following_timeline():
    """Main function to fetch and display clean timeline."""
    config = load_config()
    bearer_token = config['bearer_token']
    
    print("🔍 Fetching your clean Twitter feed...\n")
    
    # Get authenticated user
    user = get_auth_user(bearer_token)
    if not user:
        print("❌ Could not authenticate. Free tier may have limitations.")
        return
    
    print(f"Authenticated as: @{user.get('username')}\n")
    
    # Note: Free tier doesn't include home_timeline
    # We need to work around this or upgrade to Basic ($100/mo)
    
    print("⚠️  Twitter Free API tier limitation:")
    print("The free tier doesn't include the home timeline endpoint.")
    print("\nOptions:")
    print("1. Use Basic tier ($100/month) - full home timeline")
    print("2. Track specific accounts manually - I'll fetch tweets from a list you provide")
    print("3. Use RSS bridge approach (less reliable but free)")
    
    return user

def fetch_specific_users(usernames: List[str], max_per_user: int = 5):
    """Fetch tweets from specific usernames."""
    config = load_config()
    bearer_token = config['bearer_token']
    
    all_tweets = []
    
    for username in usernames:
        # First lookup user by username
        lookup_url = f"https://api.twitter.com/2/users/by/username/{username}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        
        response = requests.get(lookup_url, headers=headers)
        if response.status_code != 200:
            print(f"Could not find user: @{username}")
            continue
            
        user_data = response.json().get('data')
        if not user_data:
            continue
            
        user_id = user_data['id']
        
        # Get their tweets
        tweets = get_user_timeline(user_id, bearer_token, max_per_user)
        for tweet in tweets:
            tweet['username'] = username
            all_tweets.append(tweet)
    
    # Sort by date
    all_tweets.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return all_tweets

def display_feed(tweets: List[Dict]):
    """Display tweets in clean format."""
    if not tweets:
        print("No tweets found.")
        return
    
    print(f"\n📱 {len(tweets)} tweets\n")
    print("=" * 60)
    
    for tweet in tweets:
        username = tweet.get('username', 'unknown')
        text = tweet.get('text', '')
        created_at = tweet.get('created_at', '')
        
        if created_at:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            time_str = dt.strftime("%b %d · %I:%M %p")
        else:
            time_str = ""
        
        print(f"\n🐦 @{username}")
        print(f"   {time_str}")
        print(f"\n   {text}")
        print("\n" + "-" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "users":
        # Fetch specific users
        users = sys.argv[2:] if len(sys.argv) > 2 else []
        if not users:
            print("Usage: twitter_feed.py users <username1> <username2> ...")
            print("Example: twitter_feed.py users elonmusk navi_al")
        else:
            tweets = fetch_specific_users(users)
            display_feed(tweets)
    else:
        # Try to get auth user (shows limitation message for free tier)
        fetch_following_timeline()
        print("\nTo fetch specific users, run:")
        print("  python3 twitter_feed.py users <username1> <username2> ...")
