#!/usr/bin/env python3
"""
Heartbeat Activity Logger
Logs heartbeat activities to the activity log
Called from heartbeat processing to track system activities
"""

import sys
sys.path.insert(0, '/home/ubuntu/clawd')
from log_activity import (
    log_heartbeat, log_email_check, log_task_completed,
    log_activity, log_research, log_notion_operation
)

import argparse
from zoneinfo import ZoneInfo

EST = ZoneInfo('America/Toronto')

parser = argparse.ArgumentParser(description='Log heartbeat activities')
parser.add_argument('action', choices=[
    'heartbeat', 'email', 'task', 'morning-brief', 'afternoon-brief',
    'para-extract', 'para-tier-update', 'para-archive', 'travel-check',
    'daily-prompt', 'notion-sync', 'custom'
])
parser.add_argument('--description', '-d', help='Custom description')
parser.add_argument('--count', '-c', type=int, default=0, help='Count (emails, tasks, etc)')
parser.add_argument('--title', '-t', help='Custom title for custom action')

args = parser.parse_args()

if args.action == 'heartbeat':
    log_heartbeat(args.description or "No new activity")
    
elif args.action == 'email':
    log_email_check(args.count)
    
elif args.action == 'task':
    log_task_completed(args.description or "Task completed")
    
elif args.action == 'morning-brief':
    log_activity(
        "system", 
        "Morning brief sent", 
        args.description or "Generated and sent morning brief via Telegram"
    )
    
elif args.action == 'afternoon-brief':
    log_activity(
        "system",
        "Afternoon brief sent",
        args.description or "Generated and sent afternoon brief via Telegram"
    )
    
elif args.action == 'para-extract':
    log_activity(
        "system",
        "PARA: Fact extraction",
        args.description or f"Ran PARA fact extraction (added {args.count} facts)"
    )
    
elif args.action == 'para-tier-update':
    log_activity(
        "system",
        "PARA: Weekly tier update",
        args.description or "Updated memory tier classifications (hot/warm/cold)"
    )
    
elif args.action == 'para-archive':
    log_activity(
        "system",
        "PARA: Quarterly archive",
        args.description or "Archived cold facts for the quarter"
    )
    
elif args.action == 'travel-check':
    log_activity(
        "travel",
        "Travel countdown update",
        args.description or "Updated travel countdowns"
    )
    
elif args.action == 'daily-prompt':
    log_activity(
        "system",
        "Daily work prompt",
        args.description or "Sent daily work prioritization prompt"
    )
    
elif args.action == 'notion-sync':
    log_notion_operation(
        "Sync",
        args.description or "Synced tasks with Notion"
    )
    
elif args.action == 'custom':
    log_activity(
        "system",
        args.title or "Activity",
        args.description or "Heartbeat activity"
    )

print(f"✅ Logged: {args.action}")
