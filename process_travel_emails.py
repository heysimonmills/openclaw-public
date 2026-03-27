#!/usr/bin/env python3
import json
import base64
import re
import os
from datetime import datetime
import urllib.request
import urllib.parse

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

def check_travel_emails():
    """Check for travel-related emails."""
    tokens = refresh_token_if_needed()
    
    # Prepare API request headers
    headers = {
        'Authorization': f"Bearer {tokens['access_token']}",
        'Content-Type': 'application/json'
    }
    
    # Search for travel-related emails
    query = "subject:[TRAVEL] OR from:aircanada OR from:westjet OR from:airbnb OR from:booking.com OR from:expedia OR from:hotels.com OR from:tripadvisor OR from:delta OR from:united OR from:americanairlines"
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q={urllib.parse.quote(query)}"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        messages = result.get('messages', [])
        if not messages:
            print("No travel-related emails found.")
            return []
            
        # Get details for each message
        travel_emails = []
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
            
            # Classify the email
            email_type = classify_travel_email(subject, body)
            
            # Extract details based on email type
            details = extract_travel_details(email_type, subject, body)
            
            travel_emails.append({
                'id': msg_id,
                'subject': subject,
                'from': from_email,
                'date': date,
                'type': email_type,
                'details': details,
                'body': body[:1000] + ('...' if len(body) > 1000 else '')  # Truncate long bodies
            })
        
        return travel_emails
    except Exception as e:
        print(f"Error checking emails: {str(e)}")
        return []

def classify_travel_email(subject, body):
    """Determine what type of travel email this is."""
    subject_lower = subject.lower()
    body_lower = body.lower()
    
    # Flight classification
    if any(keyword in subject_lower or keyword in body_lower for keyword in 
           ['flight', 'booking confirmation', 'e-ticket', 'itinerary', 'airline', 'travel confirmation']):
        return 'flight'
    
    # Hotel classification
    elif any(keyword in subject_lower or keyword in body_lower for keyword in 
             ['hotel', 'reservation', 'booking.com', 'airbnb', 'stay', 'accommodation']):
        return 'hotel'
    
    # Car rental classification
    elif any(keyword in subject_lower or keyword in body_lower for keyword in 
             ['car rental', 'rental car', 'hertz', 'avis', 'enterprise', 'vehicle']):
        return 'car_rental'
    
    # General travel
    elif '[TRAVEL]' in subject:
        return 'general_travel'
    
    # Unknown
    else:
        return 'unknown'

def extract_travel_details(email_type, subject, body):
    """Extract relevant details based on email type."""
    if email_type == 'flight':
        return extract_flight_details(subject, body)
    elif email_type == 'hotel':
        return extract_hotel_details(subject, body)
    elif email_type == 'car_rental':
        return extract_car_rental_details(subject, body)
    else:
        return {}

def extract_flight_details(subject, body):
    """Extract flight details from email."""
    details = {
        'airline': 'Unknown',
        'flight_number': '',
        'departure_date': '',
        'departure_time': '',
        'departure_airport': '',
        'arrival_airport': '',
        'booking_reference': '',
        'passenger_name': ''
    }
    
    # Basic extraction with regular expressions
    # This would be much more sophisticated in a real implementation
    
    # Try to extract airline
    airline_match = re.search(r'(Air Canada|WestJet|United|American|Delta|British Airways|Lufthansa)', subject + ' ' + body)
    if airline_match:
        details['airline'] = airline_match.group(1)
    
    # Try to extract flight number
    flight_match = re.search(r'([A-Z]{2}|[A-Z]\d|\d[A-Z])\s*(\d{1,4})', body)
    if flight_match:
        details['flight_number'] = flight_match.group(0)
    
    # Try to extract booking reference
    booking_ref_match = re.search(r'(?:confirmation|reference|booking|reservation)(?:\s+(?:number|code|#))?\s*[:#]?\s*([A-Z0-9]{5,8})', body, re.IGNORECASE)
    if booking_ref_match:
        details['booking_reference'] = booking_ref_match.group(1)
    
    return details

def extract_hotel_details(subject, body):
    """Extract hotel details from email."""
    details = {
        'hotel_name': 'Unknown',
        'check_in_date': '',
        'check_out_date': '',
        'booking_reference': '',
        'guest_name': '',
        'location': ''
    }
    
    # Basic extraction with regular expressions
    # This would be much more sophisticated in a real implementation
    
    # Try to extract hotel name
    hotel_match = re.search(r'(?:at|for|with)\s+(?:the\s+)?([A-Z][A-Za-z\'\s]+(?:Hotel|Resort|Inn|Suites|Airbnb))', body)
    if hotel_match:
        details['hotel_name'] = hotel_match.group(1).strip()
    
    # Try to extract booking reference
    booking_ref_match = re.search(r'(?:confirmation|reference|booking|reservation)(?:\s+(?:number|code|#))?\s*[:#]?\s*([A-Z0-9]{5,10})', body, re.IGNORECASE)
    if booking_ref_match:
        details['booking_reference'] = booking_ref_match.group(1)
    
    return details

def extract_car_rental_details(subject, body):
    """Extract car rental details from email."""
    details = {
        'rental_company': 'Unknown',
        'pickup_date': '',
        'return_date': '',
        'booking_reference': '',
        'vehicle_type': '',
        'pickup_location': ''
    }
    
    # Basic extraction with regular expressions
    # This would be much more sophisticated in a real implementation
    
    # Try to extract rental company
    company_match = re.search(r'(Hertz|Avis|Enterprise|Budget|National|Alamo|Dollar|Thrifty)', subject + ' ' + body)
    if company_match:
        details['rental_company'] = company_match.group(1)
    
    # Try to extract booking reference
    booking_ref_match = re.search(r'(?:confirmation|reference|booking|reservation)(?:\s+(?:number|code|#))?\s*[:#]?\s*([A-Z0-9]{4,10})', body, re.IGNORECASE)
    if booking_ref_match:
        details['booking_reference'] = booking_ref_match.group(1)
    
    return details

def generate_travel_report(emails):
    """Generate a human-readable report of travel emails."""
    if not emails:
        return "No travel-related emails found."
    
    report = f"Found {len(emails)} travel-related email(s):\n\n"
    
    for i, email in enumerate(emails, 1):
        report += f"{i}. {email['subject']} (from: {email['from']})\n"
        report += f"   Type: {email['type']}\n"
        
        if email['details']:
            report += "   Details:\n"
            for key, value in email['details'].items():
                if value:  # Only include non-empty values
                    report += f"     - {key.replace('_', ' ').title()}: {value}\n"
        
        report += "\n"
    
    return report

if __name__ == "__main__":
    print("Checking for travel-related emails...")
    travel_emails = check_travel_emails()
    
    if travel_emails:
        report = generate_travel_report(travel_emails)
        print(report)
    else:
        print("No travel-related emails found.")