# PARA Migration Log - Phase 3: Personal Preferences

**Date:** 2026-01-31  
**Phase:** 3 of 3  
**Task:** Migrate Simon's personal preferences and tacit knowledge from MEMORY.md

---

## What Was Migrated

### Source
- **File:** `/home/ubuntu/clawd/MEMORY.md`
- **Sections extracted:**
  - Simon's Schedule (timezone, gym, water polo, work preferences)
  - Calendar preferences (guests-can-modify, add as attendee)
  - Communication preferences (summaries, bullet points, direct style)
  - Decision-making preferences (spending threshold, autonomy development)
  - Business context (GSG, GJC, brand voice)

### Destination
- **File:** `/home/ubuntu/clawd/life/user-preferences.md`
- **Structure:** Structured markdown (not atomic facts)
- **Rationale:** This is "how to work with Simon" operational knowledge, not entity facts

---

## Content Organized Into Sections

1. **Timezone & Time References** - EST preference, always quote in EST
2. **Schedule Patterns** - Gym, water polo, work schedule, deep work vs. meeting times
3. **Work Style & Preferences** - Time management, communication style, decision-making
4. **Calendar Preferences** - Event creation rules, email routing
5. **Personal Patterns** - Energy/focus notes, placeholders for future learning
6. **Business Context Integration** - GSG, GJC, brand voice guidelines
7. **Notes for Noah** - How to use this document, maintenance guidelines

---

## Why This Structure?

### Location: ~/life/user-preferences.md
- **Not** `areas/people/simon/` - Treating Simon as an "entity" felt inappropriate since he's the user
- **Not** scattered in resources/ - This is living, evolving operational knowledge, not reference material
- **Yes** top-level in ~/life/ - This is the most personal, frequently-referenced document for daily operations

### Format: Structured Markdown
- **Not atomic facts** - This isn't "Simon Mills founded GJC in 2025" type information
- **Operational knowledge** - "Schedule meetings after 2pm" and "Use bullet points" are how-to-work-with guidelines
- **Evolving document** - Will grow as Noah learns more patterns and preferences

---

## What Stays in MEMORY.md

**MEMORY.md should retain:**
- Accounts and access credentials (your-assistant-email@gmail.com)
- Technical system details (Notion database IDs, service URLs)
- Model tiering strategy and cost optimization
- Business operational details (client management, workflows)
- Tool-specific configurations

**MEMORY.md should NOT be:**
- The primary source for Simon's personal preferences (now in user-preferences.md)
- Duplicating schedule/calendar preferences (now in user-preferences.md)

---

## Recommendations

### 1. Update AGENTS.md
Add a line in the "Every Session" section:
```markdown
5. Read `life/user-preferences.md` — how Simon operates and prefers to work
```

### 2. Clean Up MEMORY.md (Future Task)
After confirming this migration works well, consider:
- Removing duplicated schedule/preference content from MEMORY.md
- Adding a reference: "For Simon's personal preferences and schedule, see ~/life/user-preferences.md"
- Keep only technical/system/business operational details in MEMORY.md

### 3. Evolve user-preferences.md Over Time
- Add energizers/drains as observed
- Document warning signs for stress/overload
- Track communication patterns (preferred response times, channels)
- Update schedule patterns as they change
- Archive outdated preferences

### 4. Consider Adding
- **~/life/relationships.md** - Key contacts, inner circle, relationship context (Simon mentioned this as future check-in)
- **~/life/goals.md** - Long-term goals, quarterly objectives, vision

### 5. PARA Principle Applied
This follows Nat Eliason's PARA concept where:
- **Projects** = Active work with deadlines (GSG clients, GJC launch)
- **Areas** = Ongoing responsibilities (GSG business, GJC business, personal health)
- **Resources** = Reference material (meeting notes, research)
- **Archives** = Inactive items

**user-preferences.md** is the "operating manual" that sits alongside the PARA structure — it's meta-knowledge about how to use the system effectively.

---

## Migration Complete ✓

**Files Created:**
- `/home/ubuntu/clawd/life/user-preferences.md` (3.8 KB)
- `/home/ubuntu/clawd/life/MIGRATION-LOG.md` (this file)

**Next Steps:**
- Review with Simon to confirm structure works
- Update AGENTS.md to reference user-preferences.md
- Consider future cleanup of MEMORY.md (after confirmation)
- Continue evolving user-preferences.md as patterns emerge
