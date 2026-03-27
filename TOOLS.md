# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## Calendar
- **Simon's main calendar:** your-personal-email@gmail.com
- **Simon's Hey calendar:** your-hey-email@hey.com (has recurring meetings like Cyrus)
- **GSG work calendar:** your-company-a-email@example.com (client meetings)
- **Always check ALL calendars** before scheduling: your-personal-email@gmail.com, your-hey-email@hey.com, your-company-a-email@example.com, your-company-a-gmail@gmail.com, your-sports-club@example.com
- **Always add Simon as attendee** when creating calendar events so they sync to his calendar
- **Always use `--guests-can-modify`** so Simon can edit/move events
- Events created on your-assistant-email@gmail.com (Noah's service account)

**Permissions:** Read access to all calendars. Write access limited to creating events on Noah's calendar with Simon as attendee. **Cannot delete or edit Simon's events directly** — must ask Simon to delete old events when conflicts arise.

## Flight Prices
- **SerpAPI key configured** — can query real-time Google Flights prices
- **API key location:** ~/.bashrc (SERPAPI_KEY)
- **Works for:** Any route, any date, live pricing
- **Free tier:** 100 searches/month
- **Update spreadsheet:** Prices auto-added to Google Sheets for comparison

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
