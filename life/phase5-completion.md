# Phase 5 Complete: QMD Search Setup

**Completed:** 2026-02-01  
**Task:** Set up QMD semantic search for PARA structure and implement tiered retrieval

---

## ✅ What Was Accomplished

### 1. QMD Collections Verified & Updated
- **Collections:** 3 active collections
  - `life` - PARA structure (11 files)
  - `memory` - Daily notes (19 files)
  - `clawd` - Agent configuration (15 files)
- **Total indexed:** 45 files
- **Embeddings:** 76 vectors embedded
- **Model:** embeddinggemma (local)

### 2. New Embeddings Generated
- **Updated:** 15 documents from Phase 4 entity creation
- **Chunks:** 25 chunks (53.5 KB)
- **Time:** 43 seconds
- **Method:** Local embedding model (no GPU acceleration)

### 3. Helper Scripts Created

#### a) `~/clawd/scripts/search-knowledge.sh`
Bash wrapper for QMD searches with options:
```bash
./search-knowledge.sh "Ian boyfriend"
./search-knowledge.sh -c life "water polo friends"
./search-knowledge.sh -l 10 "Good Jelly Co clients"
```

**Features:**
- Collection filtering (-c)
- Result limiting (-l)
- Help documentation (-h)

#### b) `~/clawd/scripts/tiered-retrieval.py`
Python script implementing 3-tier retrieval strategy:

**Tier 1:** Check entity summary.md first (fast, direct)
```python
python3 tiered-retrieval.py "Who is Ian?" --entity ian
```

**Tier 2:** Semantic search via QMD (when summary insufficient)
```python
python3 tiered-retrieval.py "water polo friends"
```

**Tier 3:** Load detailed atomic facts from items.json
```python
python3 tiered-retrieval.py "Tell me about Ian" --entity ian --deep
```

**Features:**
- Automatic tier progression
- Access metadata tracking (lastAccessed, accessCount)
- Category filtering for facts
- Fact update on access (for future memory decay)

---

## 🧪 Testing Results

### Test 1: Entity Search
```bash
qmd search "Ian boyfriend" -c life -n 3
```
**Result:** ✅ Found Ian's summary.md with 100% score

### Test 2: Topic Search
```bash
qmd search "water polo friends" -c life -n 3
```
**Result:** ✅ Found multiple references to water polo and schedule

### Test 3: Company Search
```bash
qmd search "Good Jelly Co collagen" -c life -n 2
```
**Result:** ✅ Found GJC summary and Jacky's relationship to GJC

### Test 4: Tiered Retrieval (Tier 1)
```bash
python3 scripts/tiered-retrieval.py "Who is Ian?" --entity ian
```
**Result:** ✅ Loaded summary.md directly (fast path)

### Test 5: Tiered Retrieval (Deep)
```bash
python3 scripts/tiered-retrieval.py "Tell me about Ian" --entity ian --deep
```
**Result:** ✅ Loaded summary + QMD search + 5 atomic facts with metadata

---

## 📊 QMD System Status

```
Documents:  45 files indexed
Vectors:    76 embedded
Collections: 3 (life, memory, clawd)
Index Size:  3.4 MB
Updated:     2026-02-01
```

### Collection Details
- **life:** 11 markdown files (PARA structure)
  - user-preferences.md
  - Migration logs
  - Entity summaries (people + companies)
- **memory:** 19 markdown files (daily notes)
- **clawd:** 15 markdown files (agent config)

---

## 🎯 Tiered Retrieval Strategy

The system now implements intelligent knowledge retrieval:

```
Query → Tier 1: Entity summary (if entity known)
      ↓ (if insufficient)
        → Tier 2: QMD semantic search
      ↓ (if deep dive needed)
        → Tier 3: Atomic facts (items.json)
```

**Benefits:**
1. **Fast:** Most queries answered by summaries
2. **Flexible:** Semantic search when entity unknown
3. **Deep:** Full fact detail available when needed
4. **Tracked:** Access metadata for future memory decay

---

## 🔄 Access Metadata Tracking

Each atomic fact now tracks:
- **lastAccessed:** Date of last retrieval
- **accessCount:** Number of times accessed

**Purpose:** Enable future memory decay (Phase 6)
- High access = resist decay (stay in summary)
- Low access + old = move to cold storage
- Never accessed + 30+ days = archive candidate

---

## 🛠️ Integration Points

### For Future Heartbeats
```python
# Quick entity check
from scripts.tiered_retrieval import search_summary
summary = search_summary("ian")

# Semantic search
from scripts.tiered_retrieval import search_qmd
results = search_qmd("upcoming calendar events", collection="memory")
```

### For Daily Workflows
```bash
# Check someone before meeting
./scripts/search-knowledge.sh -c life "Cyrus"

# Find past conversations
./scripts/search-knowledge.sh -c memory "discussed travel"

# Deep dive on a person
python3 scripts/tiered-retrieval.py "Jacky" --entity jacky --deep
```

---

## 📝 Next Steps (Future Phases)

### Phase 6: Automated Extraction (Future)
- Scan conversation transcripts for durable facts
- Auto-create entities when 3+ mentions
- Update items.json automatically
- Maintain timeline in daily notes

### Phase 7: Memory Decay (Future)
- Weekly synthesis of hot/warm/cold facts
- Rewrite summaries with recent context
- Archive cold facts while maintaining in items.json
- Frequency resistance (high accessCount stays hot)

---

## ✅ Phase 5 Status: COMPLETE

**QMD Search:** ✓ Collections updated and indexed  
**Embeddings:** ✓ 76 vectors for 45 documents  
**Search Testing:** ✓ All queries successful  
**Helper Scripts:** ✓ Bash and Python tools created  
**Tiered Retrieval:** ✓ 3-tier system implemented and tested  
**Access Tracking:** ✓ Metadata updates on fact retrieval

**Migration Status:**
- Phase 1: PARA structure ✅
- Phase 2: (Skipped - future systems)
- Phase 3: User preferences ✅
- Phase 4: People & companies ✅
- Phase 5: QMD search ✅

**All core migration phases complete!** 🎉
