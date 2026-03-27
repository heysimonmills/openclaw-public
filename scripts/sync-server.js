#!/usr/bin/env node
/**
 * sync-server.js
 *
 * Simple HTTP server that triggers push-to-convex.js when called.
 * Deploy to ~/clawd/scripts/sync-server.js on the VPS.
 *
 * Env vars:
 *   SYNC_SECRET   - Shared secret for auth (optional)
 *   SYNC_PORT     - Port to listen on (default: 3333)
 *   CONVEX_URL    - Passed through to push-to-convex.js
 *   INGEST_SECRET - Passed through to push-to-convex.js
 *
 * Systemd service:
 *   [Unit]
 *   Description=Mission Control Sync Server
 *   After=network.target
 *
 *   [Service]
 *   Type=simple
 *   User=ubuntu
 *   WorkingDirectory=/home/ubuntu/clawd/scripts
 *   ExecStart=/usr/bin/node /home/ubuntu/clawd/scripts/sync-server.js
 *   EnvironmentFile=/home/ubuntu/clawd/.env
 *   Restart=on-failure
 *   RestartSec=5
 *
 *   [Install]
 *   WantedBy=multi-user.target
 */

const http = require("http");
const { execFile } = require("child_process");
const path = require("path");

const PORT = parseInt(process.env.SYNC_PORT || "3333", 10);
const SYNC_SECRET = process.env.SYNC_SECRET || "";
const SCRIPT_PATH = path.join(__dirname, "push-to-convex.js");

let isRunning = false;

const server = http.createServer(async (req, res) => {
  // CORS headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method !== "POST") {
    res.writeHead(405, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Method not allowed" }));
    return;
  }

  // Auth check
  if (SYNC_SECRET) {
    const auth = req.headers.authorization;
    if (auth !== `Bearer ${SYNC_SECRET}`) {
      res.writeHead(401, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Unauthorized" }));
      return;
    }
  }

  // Prevent concurrent runs
  if (isRunning) {
    res.writeHead(409, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Sync already in progress" }));
    return;
  }

  isRunning = true;
  console.log(`[${new Date().toISOString()}] Sync triggered via HTTP`);

  execFile("node", [SCRIPT_PATH], {
    env: { ...process.env },
    timeout: 60000,
  }, (error, stdout, stderr) => {
    isRunning = false;

    if (error) {
      console.error(`Sync error: ${error.message}`);
      console.error(stderr);
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(JSON.stringify({
        success: false,
        error: error.message,
        stderr,
      }));
      return;
    }

    console.log(stdout);
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({
      success: true,
      output: stdout.trim(),
      timestamp: new Date().toISOString(),
    }));
  });
});

server.listen(PORT, () => {
  console.log(`Sync server listening on port ${PORT}`);
});
