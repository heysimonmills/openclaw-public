#!/usr/bin/env python3
"""
Session Activity Logger
Logs current session activities to the activity log
"""

import sys
sys.path.insert(0, '/home/ubuntu/clawd')
from log_activity import log_activity, log_development, log_notion_operation

# Log this session's activities
log_development(
    "Mission Control Dashboard", 
    "Built new Lovable-based dashboard with real-time Notion integration, Quick Capture, and model usage tracking"
)

log_development(
    "Activity Logging System",
    "Created activity_logger.py and integrated with dashboard for real-time activity tracking"
)

log_notion_operation(
    "Task management",
    "Updated Notion tasks via API: fixed Quick Capture column, enabled drag-and-drop status updates"
)

log_activity(
    "system",
    "Dashboard deployment",
    "Deployed API server and frontend, both running in tmux sessions (mc-api, lovable-dashboard)"
)

print("✅ Session activities logged!")
