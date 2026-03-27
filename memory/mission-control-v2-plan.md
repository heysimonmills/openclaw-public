# Mission Control 2.0 - Build Plan

## Project Overview
Building 7 new dashboard components for Noah's Mission Control with NextJS + Convex backend.

---

## Architecture

### Tech Stack
- **Frontend**: Next.js 16 (App Router) + TypeScript + Tailwind CSS
- **Backend**: Convex (real-time database)
- **State Management**: Convex real-time subscriptions
- **UI Components**: shadcn/ui + custom components

### Database Schema (Convex)

```typescript
// tasks.ts - Kanban Board
{
  _id: string,
  title: string,
  description?: string,
  status: "backlog" | "todo" | "in-progress" | "blocked" | "review" | "done",
  priority: "low" | "medium" | "high" | "urgent",
  category: "gjc" | "gsg" | "personal" | "travel",
  assignee?: string,
  dueDate?: number, // timestamp
  blockedReason?: string,
  tags: string[],
  notionId?: string, // link to Notion
  createdAt: number,
  updatedAt: number,
  completedAt?: number
}

// activities.ts - Real-Time Activity Stream
{
  _id: string,
  type: "task" | "email" | "travel" | "research" | "heartbeat" | "content" | "system",
  title: string,
  description?: string,
  status: "started" | "in-progress" | "completed" | "failed" | "cancelled",
  agent: string, // which agent/subagent
  sessionId?: string,
  metadata?: object, // flexible data
  startedAt: number,
  completedAt?: number,
  duration?: number, // seconds
  model?: string, // which AI model used
  cost?: number, // approximate cost
  isVisible: boolean // for filtering internal noise
}

// captures.ts - Zero-Friction Capture
{
  _id: string,
  content: string,
  type: "text" | "voice" | "link" | "image",
  source: "telegram" | "dashboard" | "voice",
  status: "new" | "processed" | "converted-to-task" | "archived",
  processedBy?: string,
  createdTaskId?: string,
  createdAt: number,
  processedAt?: number
}

// memories.ts - Memory-Connected Search
{
  _id: string,
  type: "conversation" | "fact" | "decision" | "preference" | "task-context",
  content: string,
  summary?: string,
  entities: string[], // people, companies, projects mentioned
  tags: string[],
  date: number,
  sessionId?: string,
  importance: number, // 1-10 for ranking
  vector?: number[] // for semantic search (future)
}

// content_pipeline.ts - Content Pipeline
{
  _id: string,
  platform: "linkedin" | "instagram" | "tiktok",
  contentType: "post" | "story" | "reel" | "carousel",
  status: "idea" | "draft" | "review" | "scheduled" | "posted",
  title: string,
  content?: string,
  mediaUrls?: string[],
  scheduledDate?: number,
  postedDate?: number,
  engagement?: {
    likes: number,
    comments: number,
    shares: number
  },
  createdAt: number
}

// gjc_metrics.ts - GJC Business Pulse
{
  _id: string,
  date: string, // YYYY-MM-DD
  websiteVisits: number,
  socialFollowers: {
    instagram: number,
    tiktok: number,
    linkedin: number
  },
  tasksCompleted: number,
  contentPosted: number,
  revenue?: number,
  updatedAt: number
}

// agent_status.ts - Live Agent Status
{
  _id: string,
  agentId: string,
  status: "idle" | "working" | "error" | "paused",
  currentTask?: {
    title: string,
    startedAt: number,
    progress?: number // 0-100
  },
  lastActivityAt: number,
  sessionStats: {
    totalTasks: number,
    completedToday: number,
    costToday: number
  }
}
```

---

## Build Phases

### Phase 1: Foundation (Day 1)
- [ ] Set up Convex project and schema
- [ ] Create database tables
- [ ] Set up Convex client in Next.js
- [ ] Build API layer (Convex queries/mutations)

### Phase 2: Core Components (Days 2-3)
- [ ] **Task Kanban Board** - Full drag-and-drop with @hello-pangea/dnd
- [ ] **Zero-Friction Capture** - Input component + Telegram bot integration
- [ ] **Real-Time Activity Stream** - Live updating feed with Convex subscriptions

### Phase 3: Intelligence Features (Days 4-5)
- [ ] **Memory-Connected Search** - Search across memories + activities + tasks
- [ ] **Live Agent Status** - Real-time agent monitoring dashboard
- [ ] **GJC Business Pulse** - Metrics visualization with charts

### Phase 4: Content & Polish (Days 6-7)
- [ ] **Content Pipeline** - Kanban-style content calendar
- [ ] Dashboard layout with navigation
- [ ] Real-time sync verification
- [ ] Testing and bug fixes

---

## Component Specifications

### 1. Task Kanban Board
```
Route: /tasks
Features:
- 6 columns: Backlog | To Do | In Progress | Blocked | Review | Done
- Drag-and-drop between columns
- Task cards show: title, priority badge, due date, category icon, blocker icon
- Quick add button per column
- Filter by: category, priority, assignee
- Bulk select actions
- Integration with Notion tasks (sync)
```

### 2. Real-Time Activity Stream
```
Route: /activity (enhanced)
Features:
- Live websocket updates via Convex
- Activity cards: icon, title, description, timestamp, agent, duration
- Filter by: type, agent, date range, status
- Group by: date, agent, type
- Pause/resume streaming
- Export to CSV
- Click to view full details + session logs
```

### 3. Memory-Connected Search
```
Route: /search (enhanced)
Features:
- Universal search bar (Command+K shortcut)
- Search across: memories, activities, tasks, content, calendar
- Grouped results with source badges
- Fuzzy search matching
- Recent searches
- Search suggestions
```

### 4. Zero-Friction Capture
```
Route: Global widget (floating) + /capture
Features:
- Floating capture button (bottom-right)
- Modal with: text input, voice record, quick templates
- Smart parsing: "remind me to X tomorrow" → creates task
- Telegram integration: /capture command
- Auto-categorize based on keywords
```

### 5. Live Agent Status
```
Route: /agents or sidebar widget
Features:
- Agent cards showing: name, status, current task, uptime
- Real-time activity indicators (pulsing dots)
- Today's stats: tasks completed, cost, models used
- Current session details
- Kill/pause agent buttons
```

### 6. GJC Business Pulse
```
Route: /gjc
Features:
- KPI cards: website visits, social growth, tasks completed, content posted
- 7-day trend charts
- Task completion velocity
- Content calendar preview
- Goals progress bars
- Comparison to last week
```

### 7. Content Pipeline
```
Route: /content
Features:
- Kanban columns: Ideas | Drafts | Review | Scheduled | Posted
- Cards show: platform icon, content type, title, scheduled date
- Preview modal for content
- Drag to schedule
- Calendar view toggle
- Engagement tracking (after posting)
```

---

## Implementation Strategy

### Convex Setup
```bash
# Install Convex
npm install convex
npx convex dev  # Initialize project

# Schema file: convex/schema.ts
# Functions: convex/
#   - tasks.ts (queries + mutations)
#   - activities.ts
#   - captures.ts
#   - memories.ts
#   - content.ts
#   - gjcMetrics.ts
#   - agentStatus.ts
```

### Real-Time Sync
- Use Convex `useQuery` hooks for live data
- Activities stream via `usePaginatedQuery`
- Agent status updates every 5 seconds via heartbeat

### Integration Points
1. **Notion Sync** - Python script pulls tasks → Convex
2. **Telegram Bot** - `/capture` command writes to captures table
3. **Agent Hooks** - Session spawn/completion writes to activities
4. **Memory Pipeline** - PARA facts feed into memories table

### UI Components Needed
- Drag-and-drop board (@hello-pangea/dnd)
- Real-time badges (pulsing indicators)
- Command palette (cmdk)
- Charts (recharts or tremor)
- Floating action button

---

## Success Metrics
- [ ] All 7 components functional
- [ ] Real-time updates working (< 1s latency)
- [ ] Tasks sync from Notion automatically
- [ ] Capture from Telegram works
- [ ] Search returns results in < 200ms
- [ ] Mobile responsive

---

## Dependencies to Add
```json
{
  "convex": "^1.17.0",
  "@hello-pangea/dnd": "^16.6.0",
  "cmdk": "^1.0.0",
  "@tremor/react": "^3.18.0",
  "date-fns": "^3.6.0",
  "framer-motion": "^11.0.0"
}
```
