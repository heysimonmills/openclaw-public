#!/usr/bin/env node
/**
 * push-to-convex.js
 *
 * Reads local VPS data files and POSTs them to the Convex HTTP ingestion endpoint.
 * Deploy to ~/clawd/scripts/push-to-convex.js on the VPS.
 *
 * Env vars:
 *   CONVEX_URL      - Convex deployment URL (e.g. https://xxx.convex.cloud)
 *   INGEST_SECRET   - Shared secret for /ingest endpoint auth
 *   SYNC_ALL        - Set to "true" to push all historical activities (no 24h cutoff)
 *
 * Usage:
 *   node push-to-convex.js
 *   SYNC_ALL=true node push-to-convex.js          # first-time full import
 *   CONVEX_URL=https://xxx.convex.cloud INGEST_SECRET=xxx node push-to-convex.js
 */

const fs = require("fs");
const path = require("path");
const https = require("https");
const http = require("http");

const CONVEX_URL = process.env.CONVEX_URL;
const INGEST_SECRET = process.env.INGEST_SECRET;
const HOME = process.env.HOME || "/home/ubuntu";
const SYNC_ALL = process.env.SYNC_ALL === "true" || process.argv.includes("--all");

if (!CONVEX_URL || !INGEST_SECRET) {
  console.error("Error: CONVEX_URL and INGEST_SECRET env vars are required");
  process.exit(1);
}

const INGEST_ENDPOINT = `${CONVEX_URL}/ingest`;

// =========== Data readers ===========

function readJsonl(filePath) {
  if (!fs.existsSync(filePath)) return [];
  const lines = fs.readFileSync(filePath, "utf-8").split("\n").filter(Boolean);
  const items = [];
  for (const line of lines) {
    try {
      items.push(JSON.parse(line));
    } catch {
      // skip malformed lines
    }
  }
  return items;
}

function readJson(filePath) {
  if (!fs.existsSync(filePath)) return null;
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf-8"));
  } catch {
    return null;
  }
}

// =========== Category → Type mapping ===========

const CATEGORY_TO_TYPE = {
  system: "system",
  task: "task",
  travel: "travel",
  research: "research",
  conversation: "system",
  notion: "task",
  file_operation: "system",
  development: "system",
  reminder: "system",
  email: "email",
  content: "content",
  heartbeat: "heartbeat",
};

function mapCategoryToType(category) {
  if (!category) return "task";
  return CATEGORY_TO_TYPE[category.toLowerCase()] || "system";
}

// =========== Status mapping ===========

function mapStatus(status) {
  if (!status) return "completed";
  const s = status.toLowerCase();
  if (s === "completed" || s === "complete" || s === "done") return "completed";
  if (s === "in-progress" || s === "in_progress" || s === "running") return "in-progress";
  if (s === "failed" || s === "error") return "failed";
  if (s === "cancelled" || s === "canceled") return "cancelled";
  if (s === "started" || s === "pending") return "started";
  return "completed";
}
// Parse model usage from model-usage-log.md
function parseModelUsageLog(filePath) {
  if (!fs.existsSync(filePath)) return [];
  const content = fs.readFileSync(filePath, "utf-8");
  const lines = content.split("\n");
  const stats = [];
  const today = new Date().toISOString().split("T")[0];

  for (const line of lines) {
    // Expected format: "| model | provider | queries | cost | tokens | avg | trend |"
    const match = line.match(
      /\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*(\d+)\s*\|\s*\$?([\d.]+)\s*\|\s*([\d,]+)\s*\|\s*\$?([\d.]+)\s*\|\s*([+-]?[\d.]+)%?\s*\|/
    );
    if (match) {
      const [, model, provider, queries, cost, tokens, avg, trend] = match;
      const modelName = model.trim();
      if (modelName === "Model" || modelName.startsWith("---")) continue; // skip header
      stats.push({
        model: modelName,
        provider: provider.trim(),
        totalQueries: parseInt(queries, 10),
        totalCost: parseFloat(cost),
        totalTokens: parseInt(tokens.replace(/,/g, ""), 10),
        avgCostPerQuery: parseFloat(avg),
        trend: parseFloat(trend) || 0,
        date: today,
      });
    }
  }
  return stats;
}

// Parse activity log JSONL into activities
function parseActivities(filePath) {
  const raw = readJsonl(filePath);

  // When SYNC_ALL is set, push everything; otherwise only last 24h
  const cutoff = SYNC_ALL ? 0 : Date.now() - 86400000;

  return raw
    .filter((a) => {
      const ts = new Date(a.timestamp || a.startedAt || 0).getTime();
      return ts > cutoff;
    })
    .map((a) => {
      const timestamp = new Date(a.timestamp || a.startedAt || 0).getTime();
      const isHeartbeat = (a.category || a.type || "").toLowerCase() === "heartbeat";

      return {
        type: mapCategoryToType(a.category || a.type),
        title: a.title || a.description || "Unknown activity",
        description: a.description,
        status: mapStatus(a.status),
        agent: a.agent || "noah",
        sessionId: a.sessionId,
        metadata: {
          ...(a.metadata || {}),
          sourceId: a.id || `${timestamp}-${(a.title || "").slice(0, 20)}`,
        },
        model: a.model,
        cost: a.cost || 0,
        isVisible: isHeartbeat ? false : (a.isVisible ?? true),
        startedAt: timestamp,
        completedAt: a.completedAt ? new Date(a.completedAt).getTime() : (a.status === "completed" ? timestamp : undefined),
        duration: a.duration,
      };
    });
}

// Parse heartbeat-state.json for travel events
function parseCalendarFromHeartbeat(filePath) {
  const state = readJson(filePath);
  if (!state || !state.trips) return [];

  return state.trips.map((trip) => ({
    title: trip.destination || trip.title,
    description: trip.description || `Trip to ${trip.destination}`,
    type: "travel",
    startTime: new Date(trip.departureDate || trip.startDate).getTime(),
    endTime: new Date(trip.returnDate || trip.endDate || trip.departureDate).getTime(),
    status: "scheduled",
    metadata: { destination: trip.destination, confirmation: trip.confirmation },
  }));
}

// Parse cron jobs.json for reminders
function parseRemindersFromCron(filePath) {
  const jobs = readJson(filePath);
  if (!jobs || !Array.isArray(jobs)) return [];

  return jobs
    .filter((j) => j.type === "reminder" || j.type === "one-time")
    .map((j) => ({
      title: j.title || j.name,
      description: j.description,
      type: "reminder",
      startTime: new Date(j.scheduledAt || j.runAt).getTime(),
      endTime: new Date(j.scheduledAt || j.runAt).getTime() + 1800000, // +30min
      status: "scheduled",
    }));
}

// =========== Agent Status Builder ===========

function buildAgentStatus(activityFile, cronFile, subagentFile) {
  const agents = [];
  const now = Date.now();

  // Read activity log for most recent activity
  const activities = readJsonl(activityFile);
  const lastActivity = activities.length > 0 ? activities[activities.length - 1] : null;
  const lastActivityTs = lastActivity
    ? new Date(lastActivity.timestamp || lastActivity.startedAt || 0).getTime()
    : 0;

  // Compute today's stats from activities
  const startOfDay = new Date();
  startOfDay.setHours(0, 0, 0, 0);
  const todayStart = startOfDay.getTime();

  const todayActivities = activities.filter((a) => {
    const ts = new Date(a.timestamp || a.startedAt || 0).getTime();
    return ts >= todayStart;
  });
  const completedToday = todayActivities.filter(
    (a) => (a.status || "").toLowerCase() === "completed" || (a.status || "").toLowerCase() === "done"
  ).length;
  const costToday = todayActivities.reduce((sum, a) => sum + (a.cost || 0), 0);

  // Determine noah-core status: "working" if last activity < 5 min ago
  const fiveMinAgo = now - 300000;
  const noahStatus = lastActivityTs > fiveMinAgo ? "working" : "idle";

  // Read cron jobs for metadata
  const cronJobs = readJson(cronFile);
  const cronMetadata = [];
  if (cronJobs && Array.isArray(cronJobs)) {
    for (const job of cronJobs) {
      cronMetadata.push({
        name: job.name || job.title || "Unknown job",
        schedule: job.schedule || job.cron || "",
        type: job.type || "recurring",
        lastRun: job.lastRun || job.lastRunAt || null,
        lastStatus: job.lastStatus || job.status || "unknown",
        enabled: job.enabled !== false,
      });
    }
  }

  // Build noah-core agent
  const noahCore = {
    agentId: "noah-core",
    name: "Noah",
    status: noahStatus,
    lastActivityAt: lastActivityTs || now,
    sessionStats: {
      totalTasks: activities.length,
      completedToday,
      costToday: Math.round(costToday * 100) / 100,
    },
    metadata: {
      cronJobs: cronMetadata,
      lastSync: new Date().toISOString(),
    },
  };

  // Add current task if working
  if (noahStatus === "working" && lastActivity) {
    noahCore.currentTask = {
      title: lastActivity.title || lastActivity.description || "Active task",
      startedAt: lastActivityTs,
    };
  }

  agents.push(noahCore);

  // Check for active subagents
  const subagentRuns = readJson(subagentFile);
  if (subagentRuns && Array.isArray(subagentRuns)) {
    for (const run of subagentRuns) {
      if (run.status === "running" || run.status === "active") {
        agents.push({
          agentId: `subagent-${run.id || run.name || "unknown"}`,
          name: run.name || run.type || "Subagent",
          status: "working",
          lastActivityAt: new Date(run.startedAt || now).getTime(),
          sessionStats: {
            totalTasks: run.tasksCompleted || 0,
            completedToday: run.tasksCompleted || 0,
            costToday: run.cost || 0,
          },
          currentTask: run.currentTask
            ? { title: run.currentTask, startedAt: new Date(run.startedAt || now).getTime() }
            : undefined,
        });
      }
    }
  }

  return agents;
}

// =========== Push to Convex ===========

function postToConvex(payload) {
  return new Promise((resolve, reject) => {
    const url = new URL(INGEST_ENDPOINT);
    const transport = url.protocol === "https:" ? https : http;
    const body = JSON.stringify(payload);

    const req = transport.request(
      {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname,
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${INGEST_SECRET}`,
          "Content-Length": Buffer.byteLength(body),
        },
      },
      (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            try {
              resolve(JSON.parse(data));
            } catch {
              resolve(data);
            }
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${data}`));
          }
        });
      }
    );
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

// =========== Main ===========

async function main() {
  console.log(`[${new Date().toISOString()}] Starting push-to-convex...`);
  if (SYNC_ALL) {
    console.log("  Mode: FULL SYNC (all historical data)");
  }

  const payload = {};

  // 1. Activities
  const activityFile = path.join(HOME, "clawd/data/activity-log.jsonl");
  const activities = parseActivities(activityFile);
  if (activities.length > 0) {
    payload.activities = activities;
    console.log(`  Activities: ${activities.length} items`);
  }

  // 2. Model usage
  const modelFile = path.join(HOME, "clawd/memory/model-usage-log.md");
  const modelUsage = parseModelUsageLog(modelFile);
  if (modelUsage.length > 0) {
    payload.modelUsage = modelUsage;
    console.log(`  Model usage: ${modelUsage.length} models`);
  }

  // 3. Calendar events from heartbeat
  const heartbeatFile = path.join(HOME, "clawd/memory/heartbeat-state.json");
  const tripEvents = parseCalendarFromHeartbeat(heartbeatFile);

  // 4. Reminders from cron
  const cronFile = path.join(HOME, ".clawdbot/cron/jobs.json");
  const reminderEvents = parseRemindersFromCron(cronFile);

  const calendarEvents = [...tripEvents, ...reminderEvents];
  if (calendarEvents.length > 0) {
    payload.calendarEvents = calendarEvents;
    console.log(`  Calendar events: ${calendarEvents.length} items`);
  }

  // 5. Agent status (built from real VPS state)
  const subagentFile = path.join(HOME, ".clawdbot/subagents/runs.json");
  const agentStatus = buildAgentStatus(activityFile, cronFile, subagentFile);
  if (agentStatus.length > 0) {
    payload.agentStatus = agentStatus;
    console.log(`  Agent status: ${agentStatus.length} agents`);
  }

  // Push
  if (Object.keys(payload).length === 0) {
    console.log("  No data to push.");
    return;
  }

  try {
    const result = await postToConvex(payload);
    console.log(`  Push result:`, JSON.stringify(result, null, 2));
    console.log(`[${new Date().toISOString()}] Push complete.`);
  } catch (err) {
    console.error(`  Push failed:`, err.message);
    process.exit(1);
  }
}

main();
