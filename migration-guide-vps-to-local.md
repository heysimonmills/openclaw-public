# Clawdbot Migration Guide: VPS to Local Hosting

## Overview

This guide covers migrating Clawdbot from a cloud VPS (Virtual Private Server) to a locally hosted machine. This gives you full control, reduces ongoing costs, and keeps your data on-premises.

---

## Pre-Migration Checklist

### 1. Backup Your Current Setup

**On your VPS, run:**
```bash
# Create backup directory
mkdir -p ~/clawdbot-backup-$(date +%Y%m%d)

# Backup configuration
cp -r ~/.config/clawdbot ~/clawdbot-backup-$(date +%Y%m%d)/

# Backup workspace
cp -r ~/clawd ~/clawdbot-backup-$(date +%Y%m%d)/

# Backup environment files
cp ~/.bashrc ~/clawdbot-backup-$(date +%Y%m%d)/
cp ~/.zshrc ~/clawdbot-backup-$(date +%Y%m%d)/ 2>/dev/null || true

# List installed global packages
npm list -g --depth=0 > ~/clawdbot-backup-$(date +%Y%m%d)/npm-packages.txt

# Create archive
tar -czvf ~/clawdbot-backup-$(date +%Y%m%d).tar.gz ~/clawdbot-backup-$(date +%Y%m%d)/
```

**Download the backup:**
```bash
# On your local machine
scp user@vps-host:~/clawdbot-backup-YYYYMMDD.tar.gz ~/Downloads/
```

### 2. Document Current Configuration

Note down:
- Clawdbot version: `clawdbot --version`
- Node.js version: `node --version`
- NPM packages installed globally
- API keys and tokens (store securely)
- Cron jobs: `crontab -l`
- Environment variables in `~/.bashrc` or `~/.zshrc`

---

## Hardware Requirements

### Minimum Specs
- **CPU:** 2 cores (x86_64 or ARM64)
- **RAM:** 4 GB
- **Storage:** 20 GB SSD
- **Network:** Stable internet connection with static IP (or dynamic DNS)
- **OS:** Ubuntu 22.04 LTS or newer (recommended)

### Recommended Specs
- **CPU:** 4+ cores
- **RAM:** 8 GB
- **Storage:** 50+ GB NVMe SSD
- **Network:** Gigabit ethernet, static IP preferred

---

## Step-by-Step Migration

### Step 1: Prepare Your Local Machine

**Install Ubuntu Server (recommended):**
1. Download Ubuntu Server 22.04 LTS ISO
2. Create bootable USB using Rufus (Windows) or `dd` (Mac/Linux)
3. Install on dedicated machine or VM

**Update system:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git vim htop
```

### Step 2: Install Node.js

```bash
# Install Node.js 20.x (LTS)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version  # v20.x.x
npm --version   # 10.x.x
```

### Step 3: Install Clawdbot

```bash
# Install Clawdbot globally
sudo npm install -g clawdbot

# Verify installation
clawdbot --version
clawdbot --help
```

### Step 4: Restore Configuration

```bash
# Create directories
mkdir -p ~/.config/clawdbot
mkdir -p ~/clawd

# Extract backup
tar -xzvf ~/clawdbot-backup-YYYYMMDD.tar.gz -C ~/

# Restore config
cp -r ~/clawdbot-backup-YYYYMMDD/.config/clawdbot/* ~/.config/clawdbot/

# Restore workspace
cp -r ~/clawdbot-backup-YYYYMMDD/clawd/* ~/clawd/

# Restore environment variables
# Edit ~/.bashrc and add your environment variables:
# export OPENAI_API_KEY="your-key"
# export NOTION_API_KEY="your-key"
# etc.
```

### Step 5: Install Additional Tools

```bash
# Install gog (Google Workspace CLI)
brew install steipete/tap/gogcli  # or follow gog docs

# Install other CLI tools you use
sudo apt install -y ffmpeg imagemagick

# Reinstall global npm packages from backup list
# Review npm-packages.txt and install as needed
```

### Step 6: Configure Clawdbot

```bash
# Initialize Clawdbot
clawdbot init

# Copy your config file
# If you have a custom config:
sudo cp ~/clawdbot-backup-YYYYMMDD/config.json /etc/clawdbot/

# Or use the default and reconfigure
clawdbot config
```

### Step 7: Set Up Auto-Start

**Using systemd (recommended):**

Create service file:
```bash
sudo nano /etc/systemd/system/clawdbot.service
```

Add:
```ini
[Unit]
Description=Clawdbot Agent Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/clawd
ExecStart=/usr/bin/clawdbot gateway start
Restart=always
RestartSec=10
Environment="NODE_ENV=production"

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable clawdbot
sudo systemctl start clawdbot
sudo systemctl status clawdbot
```

### Step 8: Restore Cron Jobs

```bash
# Edit crontab
crontab -e

# Add your cron jobs from the backup
# Example:
0 9 * * * cd ~/clawd && /usr/bin/node morning-brief.js
0 */6 * * * /usr/local/bin/clawdbot email-check
```

### Step 9: Network Configuration

**Option A: Static IP (Recommended)**
```bash
# Edit netplan config
sudo nano /etc/netplan/00-installer-config.yaml
```

Add:
```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

Apply:
```bash
sudo netplan apply
```

**Option B: Dynamic DNS (if no static IP)**
- Sign up for Dynamic DNS service (No-IP, DuckDNS)
- Install DDNS client:
```bash
sudo apt install ddclient
# Configure with your DDNS provider
```

### Step 10: Port Forwarding

On your router:
1. Forward port 443 (HTTPS) to your local machine's IP
2. Forward port 80 (HTTP) if using webhooks
3. Forward any custom ports Clawdbot uses

### Step 11: Update Webhook URLs

If using Telegram, Discord, or other webhooks:
1. Update bot webhook URLs to point to your new IP/domain
2. Update API callback URLs (Notion, Google, etc.)

### Step 12: Test Everything

```bash
# Check Clawdbot status
clawdbot status
clawdbot gateway status

# Test tools
clawdbot sessions list
clawdbot notion search "test"

# Send test message
clawdbot message send --target "your-chat-id" --message "Migration test!"
```

---

## Post-Migration

### 1. Update DNS Records
- Point your domain (if using one) to new IP
- Wait for DNS propagation (up to 24 hours)

### 2. Verify All Integrations
- Telegram bot
- Notion
- Google Workspace
- Any other connected services

### 3. Monitor Logs
```bash
# View Clawdbot logs
journalctl -u clawdbot -f

# Or if running directly
clawdbot logs
```

### 4. Secure Your Machine
```bash
# Enable firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 443/tcp
sudo ufw allow 80/tcp

# Set up fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban

# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd
```

### 5. Set Up Backups
```bash
# Install restic or borg for backups
sudo apt install restic

# Create backup script
# Run daily via cron
```

---

## Troubleshooting

### Clawdbot Won't Start
```bash
# Check logs
journalctl -u clawdbot --no-pager -n 100

# Check permissions
ls -la ~/.config/clawdbot/
ls -la ~/clawd/

# Reinstall if needed
sudo npm uninstall -g clawdbot
sudo npm install -g clawdbot
```

### API Keys Not Working
- Verify environment variables: `env | grep API`
- Check config file permissions
- Regenerate keys if needed

### Webhooks Not Receiving
- Verify port forwarding
- Check firewall rules
- Test with: `curl -X POST http://your-ip:port/webhook`

### High Resource Usage
```bash
# Monitor resources
htop

# Check Clawdbot processes
ps aux | grep clawdbot

# Restart if needed
sudo systemctl restart clawdbot
```

---

## Rollback Plan

If migration fails:
1. Keep VPS running until local setup is verified
2. Point DNS back to VPS IP
3. Restore VPS from snapshot (if available)
4. Debug local issues without pressure

---

## Ongoing Maintenance

**Weekly:**
- Check logs for errors
- Update system packages: `sudo apt update && sudo apt upgrade`

**Monthly:**
- Update Node.js if needed
- Update global npm packages: `sudo npm update -g`
- Review and rotate API keys
- Full backup to external storage

**Quarterly:**
- Review and clean up old logs
- Audit connected services
- Test restore from backup

---

## Summary

| Task | Time Estimate |
|------|--------------|
| Backup VPS | 15 min |
| Install local OS | 30 min |
| Install dependencies | 20 min |
| Restore config | 15 min |
| Network setup | 30 min |
| Testing | 30 min |
| **Total** | **~2.5 hours** |

---

*Generated for Simon Mills — February 2026*
