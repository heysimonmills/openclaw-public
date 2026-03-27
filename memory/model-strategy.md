# Model Strategy

## Default Model
**Claude Sonnet 4** (`anthropic/claude-sonnet-4-5`) — use for daily chat, heartbeats, routine tasks

## Opus Usage
**Claude Opus** (`anthropic/claude-opus-4-5`) — only for:
- Complex coding/debugging
- Deep analysis
- Multi-step reasoning tasks
- When Sonnet struggles with something

## Available Providers & Models
- **Anthropic:** `anthropic/claude-opus-4-5`, `anthropic/claude-sonnet-4-5`
- **OpenAI:** `openai/gpt-4o`, `openai/gpt-4o-mini`
- **Together AI:** Various open-source models (cheapest) — env: TOGETHER_API_KEY

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

## Usage Reporting
- **Monthly report:** End of each month — token usage, costs by model/provider
- **Quarterly report:** End of each quarter — trends, optimization recommendations

---

*Updated: 2026-01-31*
