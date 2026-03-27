# AI Landscape Brief: Moonshot AI (Kimi) & Together AI

*Prepared for Simon Mills - February 3, 2026*

---

## Executive Summary

**Moonshot AI (Kimi)** is a Beijing-based AI startup focused on building open-source models with massive context windows and reasoning capabilities. They represent China's competitive alternative to Western AI leaders.

**Together AI** is a San Francisco-based infrastructure platform that hosts and serves open-source AI models at scale. They're the "AWS for open-source AI" - not a model builder, but the cloud that runs them.

Both occupy different niches than Anthropic/OpenAI: Moonshot competes on performance + openness from China, while Together provides the infrastructure layer that makes open-source AI accessible.

---

## Moonshot AI (Kimi)

### Who They Are
- **Founded:** March 2023 in Beijing, China
- **Founder:** Yang Zhilin (U.S.-trained academic with background in NLP research)
- **Backing:** Alibaba, HongShan (formerly Sequoia China)
- **Product:** Kimi chatbot and K2/K2.5 open-source models

### What Makes Them Different

**1. Massive Context Windows**
- Kimi launched in October 2023 with ability to process 200,000 Chinese characters per conversation
- Can process entire books or long reports at once
- This was groundbreaking at the time (most models had 32K-128K token limits)

**2. Open-Source Philosophy**
- Released Kimi K2 (July 2025) and K2.5 (January 2026) as open-weight models
- Strong performance on coding benchmarks
- Multimodal capabilities (text, image, video understanding)

**3. Reasoning Models**
- K2.5 includes reasoning capabilities (like OpenAI's o1)
- "Kimi K2 Thinking" model released November 2025
- Competitive with Western models on benchmarks

**4. Chinese Market Focus**
- Optimized for Chinese language processing
- Part of China's push for AI sovereignty
- Growing alternative to U.S.-controlled AI

### How They Compare to Anthropic/OpenAI

| Dimension | Moonshot AI (Kimi) | Anthropic | OpenAI |
|-----------|-------------------|-----------|--------|
| **Origin** | Beijing, China (2023) | San Francisco (2021) | San Francisco (2015) |
| **Focus** | Open-source, long context | Safety-first, Constitutional AI | AGI, commercial products |
| **Models** | Kimi K2/K2.5 (open-weight) | Claude (proprietary) | GPT-4/o1 (proprietary) |
| **Philosophy** | Openness, Chinese sovereignty | Interpretable, safe AI | AGI aligned with humanity |
| **Market** | China-first, global expansion | Enterprise B2B | Consumer + Enterprise |
| **Pricing** | Very cheap (~$0.60-2.50/M tokens) | Mid-tier (~$2.50-15/M) | Mid-tier (~$2.50-60/M) |

**Key Difference:** Moonshot is positioned as China's answer to Western AI dominance. They're building competitive models that are **open** (unlike Claude/GPT) and **cost-effective** (significantly cheaper than Western alternatives).

**Why it matters:** As U.S.-China tech tensions grow, Moonshot represents a viable alternative AI stack that doesn't depend on American companies or export controls.

---

## Together AI

### Who They Are
- **Founded:** ~2022 (emerged from Together Research)
- **Based:** San Francisco, California
- **Funding:** $305M Series B (recently announced)
- **Customers:** 700,000+ developers, enterprises like Zoom, Salesforce, Quora

### What They Do

Together AI is **not an AI model company** - they're an **infrastructure platform**. Think of them as the cloud layer that makes open-source AI accessible.

**Their Platform:**
- Host and serve open-source models (Llama, Qwen, DeepSeek, etc.)
- Provide GPU clusters and serverless endpoints
- Enable developers to train, fine-tune, and deploy models
- Decentralized network of high-end GPUs across global data centers

**Recent Moves:**
- Deployed DeepSeek models in North American data centers with privacy controls
- Large-scale NVIDIA Blackwell GPU deployment
- Partnership with Cartesia for ultra-low latency voice AI
- Acquired CodeSandbox for code interpretation capabilities

### How They Compare to Anthropic/OpenAI

| Dimension | Together AI | Anthropic | OpenAI |
|-----------|------------|-----------|--------|
| **Business Model** | Infrastructure/hosting platform | Model developer | Model developer |
| **What They Sell** | GPU access + model hosting | Claude API/subscriptions | GPT API/ChatGPT subscriptions |
| **Models** | Host 100+ open-source models | Build proprietary Claude | Build proprietary GPT |
| **Philosophy** | Open-source ecosystem enabler | Safety-focused research | AGI research + deployment |
| **Customer Base** | Developers, enterprises needing custom AI | Enterprises wanting safe AI | Everyone (consumer + enterprise) |
| **Value Prop** | Cheap, flexible, open-source access | Reliable, safe, instruction-following | Most capable, widely adopted |

**Key Difference:** Together AI is **infrastructure**, not a competitor to Anthropic/OpenAI on models. They're more comparable to AWS or CoreWeave - you go to Together when you want to use **open-source** models (Llama, Qwen, etc.) without managing your own GPUs.

**Why it matters:** Together makes open-source AI economically viable at scale. They're betting that the future is open models + cheap inference, not proprietary models from big labs.

---

## The Bigger Picture: Where They Fit

### The AI Landscape (Simplified)

**Proprietary Model Leaders:**
- OpenAI (GPT-4, o1) - Consumer + enterprise, AGI mission
- Anthropic (Claude) - Enterprise-focused, safety-first
- Google (Gemini) - Integrated with Google ecosystem

**Open-Source Model Leaders:**
- Meta (Llama) - Open weights, massive adoption
- Mistral (Mixtral) - European, enterprise-focused
- **Moonshot AI (Kimi)** - China-based, long context specialist

**Infrastructure/Platform Layer:**
- **Together AI** - Open-source model hosting at scale
- AWS Bedrock - Multi-model API (proprietary + open)
- Replicate - Easy model deployment
- CoreWeave - GPU cloud for AI workloads

### Strategic Positioning

**Moonshot AI's Play:**
- Become the **Chinese alternative** to Western AI leaders
- Leverage China's AI talent + market size
- Compete on **cost** (much cheaper) and **openness** (open-weight models)
- Benefit from geopolitical tensions (companies want non-U.S. AI options)

**Together AI's Play:**
- Be the **infrastructure layer** for the open-source AI ecosystem
- Enable developers/enterprises to use cutting-edge models without vendor lock-in
- Compete on **flexibility** (100+ models), **cost** (cheaper than proprietary), and **control** (self-hosted, private)
- Bet on the long-term shift toward open-source AI

---

## Why You're Using Them

**Kimi K2.5 (Moonshot AI):**
- **Cost-effective reasoning model** (~$0.60-2.50/M vs $15/M for Claude Opus)
- Good for regular chat, calendar management, task tracking
- Reasoning capabilities for complex problems
- Fallback to pricier models (Sonnet, GPT-4o) when needed

**Together AI (for Qwen):**
- **Cheapest fallback option** (~$0.05-0.10/M tokens)
- Last-resort when everything else fails (rate limits, billing issues)
- Still capable enough for basic tasks (heartbeats, simple lookups)

**Strategic Value:**
- **Diversification** - Not dependent on Anthropic/OpenAI availability
- **Cost optimization** - Use cheaper models for routine work, expensive ones for hard problems
- **Resilience** - Automatic fallback chain means you never just stop working

---

## Bottom Line

**Moonshot AI (Kimi):** China's competitive response to OpenAI/Anthropic. Building open, cheap, capable models with reasoning. Represents geopolitical shift in AI power.

**Together AI:** The infrastructure that makes open-source AI practical. Not a model competitor - they're the platform that hosts/serves open models at scale.

**Why they matter:** Together, they represent the **alternative AI stack** - open models from diverse providers, hosted on flexible infrastructure, at a fraction of the cost of proprietary solutions. You're using them as your primary/fallback because they're cheap, capable, and diversify your risk.

---

*Questions or want to go deeper on anything? Let me know!*
