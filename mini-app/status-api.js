const http = require('http');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PORT = 18799;

// Cache for CLI results (refresh every 30s)
let cache = {
  crons: null,
  sessions: null,
  lastUpdate: 0
};

function runCLI(cmd) {
  try {
    const result = execSync(cmd, { 
      encoding: 'utf8',
      timeout: 10000,
      env: { ...process.env, HOME: '/home/ubuntu' }
    });
    return result;
  } catch (err) {
    console.error('CLI error:', err.message);
    return null;
  }
}

function updateCache() {
  const now = Date.now();
  if (now - cache.lastUpdate < 15000) return; // Cache for 15s
  
  try {
    // Get crons
    const cronsJson = runCLI('clawdbot cron list --json 2>/dev/null');
    if (cronsJson) {
      cache.crons = JSON.parse(cronsJson);
    }
  } catch (e) {
    console.error('Cache update error:', e.message);
  }
  
  cache.lastUpdate = now;
}

const server = http.createServer((req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const url = new URL(req.url, `http://localhost:${PORT}`);
  
  // Serve static files
  if (url.pathname === '/' || url.pathname === '/index.html') {
    const indexPath = path.join(__dirname, 'index.html');
    const content = fs.readFileSync(indexPath, 'utf8');
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(content);
    return;
  }
  
  // Update cache
  updateCache();
  
  // Sessions API - return basic info
  if (url.pathname === '/api/sessions') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      sessions: [{
        key: 'agent:main:main',
        updatedAt: Date.now(),
        status: 'online'
      }]
    }));
    return;
  }
  
  // Crons API
  if (url.pathname === '/api/crons') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(cache.crons || { jobs: [] }));
    return;
  }
  
  // Health check
  if (url.pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', timestamp: Date.now() }));
    return;
  }
  
  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Mini app server running on http://0.0.0.0:${PORT}`);
  // Initial cache update
  updateCache();
});
