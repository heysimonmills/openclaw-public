#!/usr/bin/env python3
import json

# Read the tracking file
tracked_threads = set()
with open('memory/email-tracking.md', 'r') as f:
    for line in f:
        if '|' in line and not line.startswith('#') and not line.startswith('YYYY'):
            parts = line.split('|')
            if len(parts) >= 2:
                thread_id = parts[1].strip()
                if thread_id and thread_id != 'Thread ID':
                    tracked_threads.add(thread_id)

print("Tracked thread IDs:", tracked_threads)
print()

# Read the current emails
with open('/tmp/current_emails.json', 'r') as f:
    current_emails = json.load(f)

# Find new unprocessed emails
new_emails = []
for email in current_emails:
    if email['threadId'] not in tracked_threads:
        new_emails.append(email)

print(f"Found {len(new_emails)} new unprocessed emails:")
for email in new_emails:
    print(f"  - {email['threadId']}: {email['subject']}")
    
# Output full details
print("\nFull details:")
print(json.dumps(new_emails, indent=2))
