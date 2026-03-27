#!/usr/bin/env python3
import json
import requests
import os

# Load Notion API key
config_path = os.path.join(os.path.dirname(__file__), 'notion_config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

API_KEY = config['api_key']

# API Constants
NOTION_API = "https://api.notion.com/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def update_page_content(page_id, blocks):
    """Update the content of a Notion page."""
    
    url = f"{NOTION_API}/blocks/{page_id}/children"
    
    payload = {
        "children": blocks
    }
    
    try:
        response = requests.patch(url, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            print(f"Successfully updated page {page_id}")
            return True
        else:
            print(f"Error updating page {page_id}: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error updating page {page_id}: {str(e)}")
        return False

# Update Amex Travel Booking
amex_booking_id = "2f644b5e-ebe5-81d0-8c5e-cfeae2d4e842"
amex_blocks = [
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Roundtrip flight booking via American Express Travel"
                    }
                }
            ]
        }
    },
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Booking Reference: 29463664"
                    }
                }
            ]
        }
    },
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Type: Roundtrip Flight"
                    }
                }
            ]
        }
    }
]
update_page_content(amex_booking_id, amex_blocks)

# Update Mexico City Return Flight
mexico_return_id = "2f644b5e-ebe5-812e-8d99-cd0aa46a14bb"
mexico_return_blocks = [
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Return flight from Mexico City to Toronto"
                    }
                }
            ]
        }
    },
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Booking Reference: SST97B"
                    }
                }
            ]
        }
    },
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Passenger: Gianni Jasper Dazo"
                    }
                }
            ]
        }
    },
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Route: Mexico City to Toronto"
                    }
                }
            ]
        }
    }
]
update_page_content(mexico_return_id, mexico_return_blocks)

# Update Montreal Hotel Stay
montreal_hotel_id = "2f644b5e-ebe5-81af-ac2a-dfe673c2f7fd"
montreal_hotel_blocks = [
    {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Hotel stay in Montreal for Simon and Gianni"
                    }
                }
            ]
        }
    },
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Date: June 6, 2026"
                    }
                }
            ]
        }
    },
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Booking Reference: ACJOLN"
                    }
                }
            ]
        }
    },
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Location: Montreal"
                    }
                }
            ]
        }
    },
    {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": "Guests: Simon Mills and Gianni Jasper Dazo"
                    }
                }
            ]
        }
    }
]
update_page_content(montreal_hotel_id, montreal_hotel_blocks)