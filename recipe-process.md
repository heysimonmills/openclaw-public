# Recipe Extraction Process

## Overview
Noah extracts recipes from Instagram video links, transcribes them, and stores them in Notion for future reference.

---

## Trigger

Simon will indicate a recipe link by:
- Prefixing with **"Recipe"** (e.g., "Recipe https://instagram.com/...")
- Or explicitly saying it's a recipe

---

## How It Works

**When Simon sends a recipe link:**

1. **Download video** using `yt-dlp`
2. **Extract audio** using `ffmpeg`
3. **Transcribe** using OpenAI Whisper API
4. **Extract title** from transcript (e.g., "Tuscan Chicken recipe" → "Tuscan Chicken")
5. **Parse ingredients** from transcript → format as list, put in Ingredients column
6. **Parse instructions** from transcript → format as bullet points (NOT paragraphs), put in Instructions column
7. **Check video description** for additional ingredients or instructions
8. **Save to Notion** Recipes database

---

## Notion Database

**Database ID:** `f44b6ca9-3236-4cef-a2f1-f8441a13fb42`
**Database URL:** https://www.notion.so/f44b6ca932364cefa2f1f8441a13fb42
**Note:** Use Notion API version `2022-06-28` for this database

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| Name | Title | Recipe name (extract from transcript, e.g., "Tuscan Chicken") |
| Source URL | URL | Original Instagram link |
| Ingredients | Rich text | Ingredient list (formatted as list, one per line) |
| Instructions | Rich text | Step-by-step instructions (formatted as bullet points, NOT paragraphs) |
| Tags | Multi-select | Chicken, Beef, Seafood, Vegetarian, Meal Prep, Quick, Asian, Italian |
| Date Added | Date | When recipe was saved |

---

## Formatting Requirements

**❗CRITICAL: Use Notion Property Columns, NOT Page Body**

**Title:**
- Extract from transcript (e.g., "so here is a Tuscan Chicken recipe" → "Tuscan Chicken")
- Put in the Title/Name column
- Clean, concise, capitalized

**Ingredients:**
- Format as a list (one ingredient per line, use • bullets)
- **MUST go in the "Ingredients" property column** (rich_text field)
- Include quantities when mentioned
- Example: "• 1 salmon portion (100g)\n• 100g cherry tomatoes\n• 60g feta cheese"

**Instructions:**
- Format as bullet points (use • or -)
- NOT paragraphs
- **MUST go in the "Instructions" property column** (rich_text field)
- Each step should be clear and actionable
- Example: "• Bake in oven for 12 minutes at 400°F"

**DO NOT put ingredients/instructions in the page body (children blocks). Only use the property columns.**

---

## Commands Used

```bash
# Download Instagram video
yt-dlp -o "recipe_video.%(ext)s" "<instagram_url>"

# Extract audio
ffmpeg -i recipe_video.mp4 -vn -acodec mp3 -ar 16000 recipe_audio.mp3

# Transcribe (using Whisper API skill)
bash /home/ubuntu/.npm-global/lib/node_modules/clawdbot/skills/openai-whisper-api/scripts/transcribe.sh recipe_audio.mp3 --out transcript.txt
```

---

## Workflow

1. Simon sends IG link → Noah downloads + transcribes
2. Noah extracts recipe details and presents for confirmation
3. Once confirmed → Save to Notion
4. Clean up temp files

---

*Last updated: 2026-01-31*
