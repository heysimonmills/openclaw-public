#!/usr/bin/env python3
"""
Comprehensive Activity Logger for Mission Control Dashboard
Captures ALL activities: tools used, research, development, conversations, tasks, etc.
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Activity log file
ACTIVITY_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'activity-log.jsonl')
DAILY_SUMMARY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'daily-summaries.json')

# Ensure data directory exists
os.makedirs(os.path.dirname(ACTIVITY_LOG_PATH), exist_ok=True)

# Activity categories
CATEGORIES = {
    'email': {'icon': 'Mail', 'color': 'blue'},
    'travel': {'icon': 'Plane', 'color': 'purple'},
    'research': {'icon': 'Search', 'color': 'cyan'},
    'development': {'icon': 'Code', 'color': 'emerald'},
    'task': {'icon': 'CheckCircle', 'color': 'green'},
    'notion': {'icon': 'FileText', 'color': 'yellow'},
    'calendar': {'icon': 'Calendar', 'color': 'pink'},
    'reminder': {'icon': 'Bell', 'color': 'orange'},
    'conversation': {'icon': 'MessageCircle', 'color': 'indigo'},
    'file_operation': {'icon': 'File', 'color': 'gray'},
    'system': {'icon': 'Settings', 'color': 'slate'},
    'api_integration': {'icon': 'Plug', 'color': 'teal'},
}

def log_activity(
    category: str,
    title: str,
    description: str = "",
    status: str = "completed",
    metadata: Optional[Dict[str, Any]] = None,
    cost: float = 0.0,
    duration_seconds: int = 0
):
    """
    Log any activity to the activity stream.
    
    Args:
        category: Type of activity (email, research, development, etc.)
        title: Short title/summary
        description: Detailed description
        status: completed, in_progress, pending, failed
        metadata: Additional structured data
        cost: Associated cost (if any)
        duration_seconds: How long the activity took
    """
    activity = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.utcnow().isoformat(),
        'category': category,
        'title': title,
        'description': description,
        'status': status,
        'metadata': metadata or {},
        'cost': cost,
        'duration_seconds': duration_seconds
    }
    
    # Append to log file (JSONL format)
    with open(ACTIVITY_LOG_PATH, 'a') as f:
        f.write(json.dumps(activity) + '\n')
    
    return activity

def get_today_activities(category: Optional[str] = None) -> list:
    """Get all activities from today."""
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).date().isoformat()
    activities = []
    
    if not os.path.exists(ACTIVITY_LOG_PATH):
        return activities
    
    with open(ACTIVITY_LOG_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                activity = json.loads(line)
                # Handle both 'Z' suffix and '+00:00' suffix
                ts = activity['timestamp']
                activity_date = ts[:10] if 'T' in ts else ts[:10]
                if activity_date == today:
                    if category is None or activity['category'] == category:
                        activities.append(activity)
            except (json.JSONDecodeError, KeyError):
                continue
    
    return sorted(activities, key=lambda x: x['timestamp'], reverse=True)

def get_recent_activities(hours: int = 24, limit: int = 50) -> list:
    """Get activities from the last N hours."""
    from datetime import timedelta
    
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    activities = []
    
    if not os.path.exists(ACTIVITY_LOG_PATH):
        return activities
    
    with open(ACTIVITY_LOG_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                activity = json.loads(line)
                activity_time = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))
                if activity_time >= cutoff:
                    activities.append(activity)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
    
    # Sort by timestamp descending and limit
    activities = sorted(activities, key=lambda x: x['timestamp'], reverse=True)
    return activities[:limit]

def get_category_breakdown(hours: int = 24) -> Dict[str, int]:
    """Get count of activities by category."""
    activities = get_recent_activities(hours=hours, limit=1000)
    breakdown = {}
    for activity in activities:
        cat = activity['category']
        breakdown[cat] = breakdown.get(cat, 0) + 1
    return breakdown

def get_daily_summary(date: Optional[str] = None) -> Dict[str, Any]:
    """Get summary statistics for a specific day."""
    if date is None:
        date = datetime.utcnow().date().isoformat()
    
    activities = []
    
    if not os.path.exists(ACTIVITY_LOG_PATH):
        return {
            'date': date,
            'total_activities': 0,
            'categories': {},
            'total_cost': 0.0,
            'by_hour': {}
        }
    
    with open(ACTIVITY_LOG_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                activity = json.loads(line)
                if activity['timestamp'][:10] == date:
                    activities.append(activity)
            except (json.JSONDecodeError, KeyError):
                continue
    
    # Calculate stats
    categories = {}
    total_cost = 0.0
    by_hour = {}
    
    for activity in activities:
        cat = activity['category']
        categories[cat] = categories.get(cat, 0) + 1
        total_cost += activity.get('cost', 0.0)
        
        hour = activity['timestamp'][11:13]
        by_hour[hour] = by_hour.get(hour, 0) + 1
    
    return {
        'date': date,
        'total_activities': len(activities),
        'categories': categories,
        'total_cost': round(total_cost, 2),
        'by_hour': by_hour
    }

def export_to_dashboard_format() -> list:
    """Export recent activities in dashboard-compatible format."""
    activities = get_recent_activities(hours=24, limit=100)
    
    dashboard_activities = []
    for activity in activities:
        cat_config = CATEGORIES.get(activity['category'], CATEGORIES['system'])
        
        dashboard_activities.append({
            'id': activity['id'],
            'timestamp': activity['timestamp'],
            'type': activity['category'],
            'title': activity['title'],
            'description': activity['description'],
            'status': activity['status'],
            'icon': cat_config['icon'],
            'color': cat_config['color'],
            'metadata': activity['metadata']
        })
    
    return dashboard_activities

# Convenience functions for common activity types
def log_research(query: str, source: str = "web_search", results_count: int = 0):
    """Log a research activity."""
    return log_activity(
        category='research',
        title=f"Research: {query[:60]}..." if len(query) > 60 else f"Research: {query}",
        description=f"Searched for: {query}",
        metadata={'source': source, 'results_count': results_count}
    )

def log_development(task: str, file_path: str = "", language: str = ""):
    """Log a development/coding activity."""
    return log_activity(
        category='development',
        title=f"Development: {task}",
        description=f"Worked on: {task}" + (f" ({file_path})" if file_path else ""),
        metadata={'file': file_path, 'language': language}
    )

def log_task_completed(task_name: str, project: str = "", notes: str = ""):
    """Log a completed task."""
    return log_activity(
        category='task',
        title=f"✓ {task_name}",
        description=notes or f"Completed task: {task_name}",
        status='completed',
        metadata={'project': project}
    )

def log_notion_operation(operation: str, page_title: str = ""):
    """Log a Notion operation."""
    return log_activity(
        category='notion',
        title=f"Notion: {operation}",
        description=f"{operation}" + (f" - {page_title}" if page_title else ""),
        metadata={'page': page_title}
    )

def log_file_operation(operation: str, file_path: str, description: str = ""):
    """Log a file operation (read, write, edit)."""
    return log_activity(
        category='file_operation',
        title=f"File {operation}: {os.path.basename(file_path)}",
        description=description or f"{operation} operation on {file_path}",
        metadata={'file': file_path, 'operation': operation}
    )

def log_conversation(topic: str, channel: str = "telegram"):
    """Log a conversation/interaction."""
    return log_activity(
        category='conversation',
        title=f"Chat: {topic[:50]}..." if len(topic) > 50 else f"Chat: {topic}",
        description=f"Conversation about {topic}",
        metadata={'channel': channel}
    )

def log_api_integration(service: str, action: str, status: str = "completed"):
    """Log an API integration activity."""
    return log_activity(
        category='api_integration',
        title=f"API: {service} - {action}",
        description=f"Integrated with {service}: {action}",
        status=status,
        metadata={'service': service, 'action': action}
    )

def log_system_operation(operation: str, details: str = ""):
    """Log a system operation (restart, setup, etc)."""
    return log_activity(
        category='system',
        title=f"System: {operation}",
        description=details or operation,
        metadata={'operation_type': operation}
    )

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "today":
            activities = get_today_activities()
            print(f"Today's activities ({len(activities)}):")
            for a in activities[:20]:
                print(f"  [{a['category']}] {a['title']}")
        
        elif command == "summary":
            summary = get_daily_summary()
            print(json.dumps(summary, indent=2))
        
        elif command == "export":
            dashboard_data = export_to_dashboard_format()
            print(json.dumps(dashboard_data, indent=2))
    else:
        # Test logging
        log_activity('test', 'Activity logger test', 'Testing the activity logger')
        print("Test activity logged. Run 'python3 activity_logger.py today' to see it.")
