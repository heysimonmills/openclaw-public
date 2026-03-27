# MEMORY.md - Noah's Long-Term Memory

> **Note:** As of 2026-02-01, structured knowledge has migrated to the PARA system at `~/life/`.
> - **User preferences, schedule, work style:** See `~/life/user-preferences.md`
> - **People & companies:** See `~/life/areas/people/` and `~/life/areas/companies/`
> - **Projects:** See `~/life/projects/`
>
> This file now contains system-level info and legacy context not yet migrated.

## Accounts and Access

### Google Account
- Email: your-assistant-email@gmail.com
- Password: [STORE IN .env OR SECRETS MANAGER — NEVER COMMIT PLAINTEXT PASSWORDS]
- Purpose: Calendar management, email access

## Email Routing

### Calendar Invites
- Company A matters → [YOUR_COMPANY_A_EMAIL]
- Personal matters → [YOUR_PERSONAL_EMAIL]
- Company B matters → [YOUR_COMPANY_B_EMAIL]

## Calendar System
- User has shared calendars with the assistant's Google account
- Access type: Full view access to schedule
- Permission to create and send calendar invites

## User's Schedule

**See:** `~/life/user-preferences.md` for timezone, gym, work preferences, and current client work.

## Regular Tasks
- Check calendar for upcoming events
- Send reminders for important appointments

## Model Tiering (Cost Optimization)

| Tier | Model | Use For |
|------|-------|---------|
| Cheapest | together/meta-llama/Llama-3.3-70B-Instruct-Turbo | Heartbeats, email checks |
| Cheap | openai/gpt-4o-mini | Calendar, Notion basics |
| Mid | anthropic/claude-sonnet-4 or openai/gpt-4o | Research, travel processing |
| High | anthropic/claude-opus-4-5 | Direct convos with user, complex analysis |

- Log usage in `memory/model-usage-log.md`
- Monthly summary on 28th
- Quarterly review on 1st of Jan/Apr/Jul/Oct

## Travel Management
- Notion Database ID: [YOUR_NOTION_TRAVEL_DB_ID]
- Process documented in `travel-process.md`
- Fields: Name, Travel Dates, Type, Confirmation Number, Destination

## Flight Search Process

### Tools Available
- **SerpAPI**: Configured with API key for Google Flights data
- **Free tier**: 100 searches/month
- **Provides**: Live prices, flight times, airlines, flight numbers

### Required Steps (in order)
1. **Query SerpAPI** for live prices (not estimates)
2. **Create spreadsheet** immediately after getting data
3. **SHARE IMMEDIATELY** with user's email + make public
4. **Format properly** with clear column headers
5. **Label currency** clearly in headers and data
6. **Organize logically** (outbound → return → best combo)

### Common Mistakes to Avoid
- ❌ Don't give estimates from web search
- ❌ Don't delay sharing until asked
- ❌ Don't create messy/unreadable formatting
- ❌ Don't forget currency labels

### Quick Reference
```python
# SerpAPI query for flights
params = {
    "engine": "google_flights",
    "departure_id": "YOUR_DEPARTURE_CODE",
    "arrival_id": "YOUR_ARRIVAL_CODE",
    "outbound_date": "YYYY-MM-DD",
    "return_date": "YYYY-MM-DD",
    "currency": "CAD",
    "hl": "en",
    "api_key": SERPAPI_KEY
}
```

## Mission Control Mini App
- URL: `http://YOUR_SERVER_IP:PORT` or `https://your-domain.com`
- Service: `noah-mini-app.service`
- Shows agent status, subagents, cron jobs

## Calendar Preferences

**See:** `~/life/user-preferences.md` for calendar rules and preferences.

## Business Context

**See:**
- Company A: `~/life/areas/companies/company-a/`
- Company B: `~/life/areas/companies/company-b/`
- Person E (co-founder): `~/life/areas/people/person-e/`

## Communication & Decision Making

**See:** `~/life/user-preferences.md` for permissions, autonomy, communication preferences, and decision-making patterns.
