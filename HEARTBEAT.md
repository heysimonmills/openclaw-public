# HEARTBEAT TASKS

## Activity Logging
**Log all heartbeat activities to dashboard:**
- After any significant action, run: `python3 ~/clawd/heartbeat_logger.py <action>`
- Actions: `heartbeat`, `email`, `morning-brief`, `afternoon-brief`, `para-extract`, `travel-check`, `daily-prompt`, `notion-sync`
- Use `--description "..."` for custom details
- Use `--count N` for countable items (emails, facts, etc)

## Email Checking
- Check your-email@gmail.com for new emails
- **Before alerting:** Check `memory/email-tracking.md` - if thread ID already logged, skip it
- If new unprocessed emails found, alert Simon with a summary
- **For (TRAVEL) emails:** Run `travel-process.md` instead of just alerting
- For emails requiring response, propose draft replies for approval
- Never respond to emails automatically
- **After processing:** Log thread ID, subject, and action to `memory/email-tracking.md`
- **Log activity:** `python3 ~/clawd/heartbeat_logger.py email --count <N>`

## PARA Memory Maintenance
- **Daily (once per day):** Extract new facts from conversations
  - Run: `python3 ~/life/.scripts/extract-facts.py --auto`
  - Check last run in `memory/heartbeat-state.json`
  - Only run if >24h since last extraction
  - **Log:** `python3 ~/clawd/heartbeat_logger.py para-extract --count <N>`

- **Weekly (Mondays):** Update memory tiers
  - Run: `python3 ~/life/.scripts/memory-decay.py --execute`
  - Updates hot/warm/cold classifications
  - Check if today is Monday before running
  - **Log:** `python3 ~/clawd/heartbeat_logger.py para-tier-update`

- **Quarterly (1st of Jan/Apr/Jul/Oct):** Archive cold facts
  - Run: `~/life/.scripts/run-maintenance.sh --commit`
  - Full maintenance + git commit
  - Check if it's the 1st of a quarter month
  - **Log:** `python3 ~/clawd/heartbeat_logger.py para-archive`

## Maintenance
- Keep track of last check times to avoid duplicate alerts
- Rotate through checks to avoid excessive API calls
- Track PARA maintenance runs in `memory/heartbeat-state.json`

## Daily Work Prompt (NEW)
- **Time:** 9:00 AM daily (after morning brief)
- **Action:** Prompt Simon with what I should start working on
- **Format:** "💡 Daily Check-in: What should I prioritize today? Based on my task list, I'm considering: [list current tasks]. What would you like me to focus on?"

## Important Notes
- **DO send:** Morning briefs, afternoon briefs, email alerts (travel emails, important messages), daily work prompt
- **DO NOT send:** Individual calendar event notifications/reminders (e.g. "Meeting in 1 hour")
- Exception: Morning/afternoon briefs can include today's calendar overview - that's different from event-by-event pings