# Task Management Process

## Overview

Noah manages Simon's tasks using Notion's "Daily To Dos" database with automated reminders and calendar blocking. This document outlines the complete process.

---

## 1. Task Tracking in Notion

**Where tasks live:**
- All tasks tracked in Notion "Daily To Dos" database
- Task entries include name, category, due date, status, and priority

**Task Categories:**
- **GSG:** George St Growth tasks (💼 GSG)
- **GJC:** Good Jelly Co tasks (🍯 GJC)
- **Personal:** Personal tasks (🏠 Personal)

**Task Statuses:**
- Not started
- In progress
- Completed
- Archived

---

## 2. Adding Tasks

**IMPORTANT: Check for duplicates first!**
Before creating a new task, always search Notion to see if it already exists:
```bash
python3 notion_tasks.py list | grep -i "[keyword]"
```

**How tasks are added:**
- Simon sends task via message: "Add task: [task details]"
- Simon shares daily/tomorrow's plan (group of tasks)
- Noah proactively identifies tasks from conversations

**Required information:**
- Task name (always required)
- Category (GSG/GJC/Personal - guess if not specified, confirm with Simon)
- Due date (ask if not specified)
- Priority (optional)

**Handling due dates:**
- Specific date format: YYYY-MM-DD
- "Today" → Current date
- "Tomorrow" → Next day
- "Next week" → Current date + 7 days
- If uncertain → Ask Simon

---

## 3. Daily Planning

**Evening before / Morning of:**
- Simon sends "tomorrow's plan" or "plan for today"
- Noah adds all tasks to Notion with appropriate due dates
- Tasks organized by category and priority

**Calendar blocking:**
- When requested, Noah blocks time in calendar for specific tasks
- Takes into account Simon's existing commitments
- Respects meeting preferences (after 2pm EST)
- Preserves deep work time in mornings

---

## 4. Follow-ups and Reminders

**Morning brief (7:00 AM EST daily):**
- Uses `get_daily_tasks.py` to fetch today's + overdue tasks from Notion
- Includes formatted task list in Telegram message
- Provides link to Notion database for full view
- Also includes: calendar, weather, reminders

**Task list format:**
```
📋 Tasks for [Date]

⚠️ Overdue: (if any)
  • [Category] Task name (Priority) (X days ago)

📅 Due Today:
  • [Category] Task name (Priority)

📎 View in Notion: [link]
```

**Evening brief (6:00 PM EST daily):**
- Recap completed tasks
- Preview tomorrow's schedule
- Flag any overdue items

---

## 5. Task Management Commands

| Command | Action |
|---------|--------|
| `python3 notion_tasks.py add [task_name] [category] [status] [priority] [due_date]` | Add new task |
| `python3 notion_tasks.py list` | List all tasks |
| `python3 notion_tasks.py list-status "Not started"` | List tasks by status |
| `python3 notion_tasks.py update-status [task_name] [new_status]` | Update task status |
| `python3 notion_tasks.py update-category [task_name] [category]` | Update task category |

**Categories:** GSG, GJC, Personal (case-insensitive shortcuts supported)

---

## 6. Example Workflow

1. Simon: "Add a task for GJC: update website copy for tomorrow"
2. Noah: Runs `python3 notion_tasks.py add "Update website copy" GJC "Not started" "" "2026-02-04"`
3. Task created in Notion with category "🍯 GJC" and due date set to tomorrow
4. Simon: "Can you block time for me to work on this?"
5. Noah: Creates calendar event in appropriate calendar, respecting work preferences
6. Noah: Includes task in morning reminder the following day
7. Simon: Completes task and reports back
8. Noah: Runs `python3 notion_tasks.py update-status "Update website copy" "Done"` immediately

---

## 7. Automatic Status Updates

**CRITICAL:** When Simon reports task completion, immediately update Notion without being asked.

**Trigger phrases:**
- "I finished [task]"
- "I completed [task]"
- "I've done [task]"
- "Just finished [task]"
- "[Task] is done"

**Action:**
1. Immediately run: `python3 notion_tasks.py update-status "[task_name]" "Done"`
2. Confirm the update to Simon
3. Do NOT wait to be asked to update Notion

---

## 8. Key Principles

1. **Always categorize properly** - GSG, GJC, or Personal is required for every task
2. **Confirm ambiguous information** - When uncertain about category or due date, ask
3. **Proactive reminders** - Flag approaching deadlines without being asked
4. **Single source of truth** - Notion database is the master record of all tasks
5. **Respect schedule preferences** - Deep work in mornings, meetings after 2pm EST
6. **Auto-update on completion** - When Simon reports finishing a task, update Notion immediately

---

*Last updated: 2026-02-03*