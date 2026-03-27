# Memory System Upgrade: PARA + Atomic Facts + QMD

**Goal:** Implement Nat Eliason's agentic PKM system for durable, structured memory

**Reference:** https://x.com/nateliason/status/2017636775347331276

---

## Current State

### What We Have
- Daily notes in `memory/YYYY-MM-DD.md`
- Long-term memory in `MEMORY.md` (flat list)
- Tacit knowledge in `AGENTS.md`, `SOUL.md`, `USER.md`
- `memory_search` tool for semantic search

### What's Missing
- PARA directory structure for knowledge graph
- Atomic facts with metadata (timestamps, superseding, access counts)
- Memory decay (hot/warm/cold tiers)
- QMD search integration
- Automated fact extraction from conversations

---

## Implementation Plan

### Phase 1: Directory Structure (Week 1)
- [ ] Create `life/` directory with PARA structure:
  - `projects/` — Active work with goals/deadlines
  - `areas/` — Ongoing responsibilities (people, companies)
  - `resources/` — Reference material
  - `archives/` — Completed/inactive items
- [ ] Create `life/index.md` and `life/README.md`
- [ ] Migrate existing entities from MEMORY.md to appropriate folders

### Phase 2: Entity Schema (Week 1-2)
- [ ] Define atomic fact schema:
  ```json
  {
    "id": "string",
    "fact": "string",
    "category": "relationship|milestone|status|preference|context",
    "timestamp": "YYYY-MM-DD",
    "source": "YYYY-MM-DD (daily note ref)",
    "status": "active|superseded",
    "supersededBy": "fact-id or null",
    "relatedEntities": ["path/to/entity"],
    "lastAccessed": "YYYY-MM-DD",
    "accessCount": 0
  }
  ```
- [ ] Create template for `summary.md` + `items.json`
- [ ] Start with 3-5 key entities (Ian, Jacky, George St Growth, Good Jelly Co, key projects)

### Phase 3: QMD Setup (Week 2)
- [ ] Install QMD: `brew install qmd` or build from source
- [ ] Create collections:
  - `qmd collection add ~/life --name life --mask "**/*.md"`
  - `qmd collection add ~/clawd/memory --name memory --mask "**/*.md"`
  - `qmd collection add ~/clawd --name clawd --mask "*.md"`
- [ ] Run initial indexing: `qmd update && qmd embed`
- [ ] Test search: `qmd query "test query"`

### Phase 4: Retrieval Integration (Week 2-3)
- [ ] Create helper scripts for QMD queries
- [ ] Update memory retrieval to use tiered approach:
  1. Check entity `summary.md` first
  2. Query QMD if summary insufficient
  3. Load specific facts from `items.json`
- [ ] Track access metadata when facts are retrieved

### Phase 5: Automated Extraction (Week 3-4)
- [ ] Design heartbeat extraction process:
  - Scan recent conversation transcripts
  - Identify durable facts (relationships, milestones, decisions, preferences)
  - Write to appropriate entity `items.json`
  - Update daily notes with timeline entries
  - Bump access metadata
- [ ] Create entity creation heuristics (3+ mentions, direct relationship, significant)
- [ ] Run extraction on conversation history

### Phase 6: Memory Decay (Week 4)
- [ ] Implement weekly synthesis:
  - Load all active facts from each entity
  - Sort into Hot (0-7 days) / Warm (8-30 days) / Cold (31+ days)
  - Rewrite `summary.md` with Hot + Warm facts
  - Keep Cold facts in `items.json` only
- [ ] Add frequency resistance (high accessCount resists decay)
- [ ] Schedule weekly cron job

### Phase 7: Migration & Testing (Week 5)
- [ ] Migrate all MEMORY.md content to PARA structure
- [ ] Test retrieval across all layers
- [ ] Validate no information loss
- [ ] Run heartbeat extraction on last 30 days of conversations
- [ ] Monitor performance and token usage

---

## Key Principles

1. **No deletion** — Facts are superseded, never deleted
2. **Tiered retrieval** — Summary first, then search, then full facts
3. **Graceful degradation** — Daily notes are always the fallback
4. **Natural lifecycle** — Entities and facts flow through states
5. **Low-tech backbone** — Plain files, git-backed, portable

---

## Questions to Resolve

- [ ] Where should `life/` directory live? `/home/ubuntu/life`?
- [ ] Backup strategy for PARA structure?
- [ ] Weekly synthesis timing (which day/time)?
- [ ] Token budget for automated extraction?

---

**Status:** Planning
**Started:** 2026-01-31
**Target Completion:** ~5 weeks
