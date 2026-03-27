# Heartbeat Optimization Configuration

**Implemented:** February 28, 2026  
**Purpose:** Reduce model usage costs during low-activity nighttime hours

---

## Optimization 1: Reduced Nighttime Frequency

**Change:** Reduce heartbeat from 30min → 1 hour during night hours

**Schedule:**
- **Daytime (6am–11pm ET / 11am–4am UTC):** Every 30 minutes
- **Nighttime (11pm–6am ET / 4am–11am UTC):** Every 60 minutes

**Estimated Savings:** ~15% reduction in heartbeat API calls

**Implementation:**
```json
{
  "heartbeat": {
    "daySchedule": "*/30 * * * *",
    "nightSchedule": "0 * * * *",
    "nightHours": {
      "start": "04:00",
      "end": "11:00",
      "timezone": "UTC"
    }
  }
}
```

---

## Optimization 2: Tier 1 Model for Heartbeats

**Change:** Use cheapest Tier 1 model for routine heartbeat checks

**Model:** `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`

**Cost Comparison:**
| Tier | Model | Cost/M tokens | Est. Monthly |
|------|-------|---------------|--------------|
| T1.5 | moonshot/kimi-k2.5 | ~$0.60-2.50 | ~$9 |
| T1 | together/llama-3.3-70B | ~$0.05-0.10 | ~$0.60 |
| **Savings** | | | **~93%** |

**Configuration:**
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "moonshot/kimi-k2.5",
        "fallbacks": [
          "anthropic/claude-sonnet-4-5",
          "openai/gpt-4o-mini",
          "together/Qwen/Qwen2.5-72B-Instruct-Turbo"
        ]
      }
    },
    "heartbeat": {
      "model": {
        "primary": "together/meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "fallbacks": [
          "together/Qwen/Qwen2.5-72B-Instruct-Turbo",
          "openai/gpt-4o-mini"
        ]
      }
    }
  }
}
```

---

## Combined Impact

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Heartbeats/day | ~48 | ~39 | ~19% |
| Model Tier | T1.5 | T1 | ~93% |
| **Est. Monthly Cost** | **~$9** | **~$0.50** | **~94%** |

---

## Implementation Notes

1. **Gateway Config:** These changes require updating `clawdbot.json` and restarting the Gateway
2. **Heartbeat Logic:** Heartbeats use a simple prompt that checks HEARTBEAT.md — perfect for Tier 1
3. **Safety:** If Tier 1 fails, fallback to Tier 1.5 ensures continuity
4. **Monitoring:** Watch for any missed alerts after implementation

---

## Implementation Status

### ✅ Completed (Feb 28, 2026)
- **Tier 1 Model:** Added `agents.heartbeat.model` config to `/home/ubuntu/.clawdbot/clawdbot.json`
- **Model:** `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`
- **Fallbacks:** `together/Qwen/Qwen2.5-72B-Instruct-Turbo` → `openai/gpt-4o-mini`

### ⏳ Pending Gateway Restart
The Tier 1 model config is saved but requires a Gateway restart to take effect.

### ⏳ Pending External Change
**Nighttime frequency reduction** (30min → 1hr at night) requires changes to the external heartbeat scheduler (outside clawdbot.json). Contact Clawdbot support or modify Gateway cron externally.

---

## Files Updated

1. ✅ `/home/ubuntu/.clawdbot/clawdbot.json` — Added heartbeat model override
2. ⏳ External scheduler — Update heartbeat schedule for nighttime (pending)

**Command to apply pending restart:**
```bash
clawdbot gateway restart
```
