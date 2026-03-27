# Model Tiering Framework

## Purpose
Use cheaper models for routine tasks to reduce costs while keeping Opus for complex work and direct conversations.

## Tiers

### Tier 1: Cheapest (Simple Routine Tasks)
**Models:** `together/meta-llama/Llama-3.3-70B-Instruct-Turbo` or `together/Qwen/Qwen2.5-72B-Instruct-Turbo`
**Cost:** ~$0.05-0.10/M input tokens

**Use for:**
- **Heartbeat checks** (now default — implemented Feb 28, 2026)
- Simple status checks
- Basic formatting

### Tier 1.5: Cheap (Routine Tasks)
**Models:** `openai/gpt-4o-mini` or `anthropic/claude-3-5-haiku-latest`
**Cost:** ~$0.15-0.25/M input tokens

**Use for:**
- Calendar event creation
- Basic Notion updates
- Simple lookups
- Slightly more complex formatting

### Tier 2: Mid (Moderate Complexity)
**Models:** `openai/gpt-4o` or `anthropic/claude-sonnet-4-5`
**Cost:** ~$2.50-3/M input tokens

**Use for:**
- Travel email processing
- Research tasks
- Content writing/editing
- Data extraction from documents
- Multi-step Notion operations
- Web scraping/browser tasks

### Tier 3: High (Complex Reasoning)
**Models:** `anthropic/claude-opus-4-5`
**Cost:** ~$15/M input tokens

**Use for:**
- Complex coding/debugging
- Security audits
- Deep analysis requiring nuanced judgment
- Architecture decisions
- Sensitive operations
- When Tier 2 models struggle with a task

## Decision Framework

When evaluating a task:
1. **Is it complex reasoning, coding, or security-sensitive?** → Tier 3 (Opus)
2. **Is it regular chat, multi-step tasks, research?** → Tier 2 (Sonnet/GPT-4o)
3. **Is it routine/repetitive (heartbeats, simple lookups)?** → Tier 1 (cheapest)

**Default for direct chat with Simon:** Tier 2 (Sonnet/GPT-4o)

## Implementation

### Sub-Agent Model Selection

When spawning sub-agents, **always** select the appropriate tier based on task complexity:

**Tier 1 tasks:**
```
sessions_spawn(task="...", model="together/meta-llama/Llama-3.3-70B-Instruct-Turbo")
```

**Tier 1.5 tasks:**
```
sessions_spawn(task="...", model="openai/gpt-4o-mini")
```

**Tier 2 tasks:**
```
sessions_spawn(task="...", model="openai/gpt-4o")
```

**Tier 3 tasks:**
```
sessions_spawn(task="...", model="anthropic/claude-opus-4-5")
```

### Examples
- Heartbeat email check → Tier 1 (Llama)
- Calendar event creation → Tier 1.5 (GPT-4o-mini)
- Recipe extraction batch → Tier 2 (GPT-4o)
- Complex debugging → Tier 3 (Opus)

## Fallback Protocol
When an API call fails, pick the right fallback chain based on the error:

### Request Too Large — try same-tier with higher limits first
| Starting model | 1st fallback | 2nd fallback | 3rd fallback |
|---|---|---|---|
| `anthropic/claude-opus-4-5` | `anthropic/claude-sonnet-4-5` | `openai/gpt-4o` | `openai/gpt-4o-mini` |
| `anthropic/claude-sonnet-4-5` | `openai/gpt-4o` | `openai/gpt-4o-mini` | Together AI |
| `openai/gpt-4o` | `anthropic/claude-sonnet-4-5` | `openai/gpt-4o-mini` | Together AI |

### Rate Limit (429) / Token Quota / Credit Error — go cheaper
| Starting model | 1st fallback | 2nd fallback | 3rd fallback |
|---|---|---|---|
| `anthropic/claude-opus-4-5` | `anthropic/claude-sonnet-4-5` | `openai/gpt-4o-mini` | Together AI |
| `anthropic/claude-sonnet-4-5` | `openai/gpt-4o-mini` | Together AI | — |
| `openai/gpt-4o` | `openai/gpt-4o-mini` | Together AI | — |

### Behavior
1. Automatically switch to the next model in the relevant chain
2. Continue working — do not stop or wait
3. Log the switch in today's `memory/YYYY-MM-DD.md` (model, error, replacement)
4. Alert Simon only if you drop 2+ tiers or **all providers fail**

---
*Created: 2026-01-29*
