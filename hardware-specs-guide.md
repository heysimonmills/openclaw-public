# Hardware Requirements Guide
## Running Clawdbot + Seedbox + Media Server

---

## Overview

This guide outlines the hardware specifications needed to run three services simultaneously on a single machine:

1. **Clawdbot** — Your AI assistant and automation platform
2. **Seedbox** — BitTorrent client for downloading/seeding
3. **Media Server** — Plex/Jellyfin for streaming media

---

## Three Configuration Options

### Option 1: Budget Build (~$300-500)
*Good for: Clawdbot + light seedbox + media server for 1-2 users*

| Component | Specs | Notes |
|-----------|-------|-------|
| **CPU** | Intel i3-10100 / AMD Ryzen 3 3200G | 4 cores, integrated graphics |
| **RAM** | 8 GB DDR4 | Single stick okay, dual-channel better |
| **Storage (OS)** | 120 GB SSD | SATA or NVMe |
| **Storage (Media)** | 2-4 TB HDD | 5400 RPM minimum, 7200 RPM preferred |
| **Network** | Gigabit Ethernet | Must have stable internet |
| **Power Supply** | 300W 80+ Bronze | Don't cheap out here |
| **Case** | Any mini-ITX or micro-ATX | Ensure good airflow |

**Estimated Power Draw:** 30-60W idle, 80-120W under load

---

### Option 2: Recommended Build (~$600-900)
*Good for: Clawdbot + active seedbox + media server for 3-5 concurrent users*

| Component | Specs | Notes |
|-----------|-------|-------|
| **CPU** | Intel i5-12400 / AMD Ryzen 5 5600G | 6 cores, excellent efficiency |
| **RAM** | 16 GB DDR4 (2x8GB) | Dual-channel for better performance |
| **Storage (OS/Apps)** | 256 GB NVMe SSD | Fast boot and app loading |
| **Storage (Media)** | 4-8 TB HDD (or NAS) | Consider 2x drives for redundancy |
| **Network** | Gigabit Ethernet | Cat6 cables, gigabit router |
| **Power Supply** | 450W 80+ Gold | Efficiency matters for 24/7 operation |
| **Case** | Fractal Design Node 304 / SilverStone | Hot-swappable bays ideal |

**Estimated Power Draw:** 35-70W idle, 100-150W under load

---

### Option 3: High-Performance Build (~$1200-1800)
*Good for: Clawdbot + heavy seedbox (1000+ torrents) + 4K media server for 10+ users*

| Component | Specs | Notes |
|-----------|-------|-------|
| **CPU** | Intel i5-13500 / AMD Ryzen 7 5700G | 8+ cores, hardware transcoding |
| **RAM** | 32 GB DDR4 (2x16GB) | Future-proof, handles many transcodes |
| **Storage (OS/Apps)** | 500 GB NVMe SSD | Samsung 980 Pro or similar |
| **Storage (Media)** | 8-16 TB (multiple drives) | Consider RAID/ZFS setup |
| **Storage (Cache)** | 1 TB NVMe SSD | For seedbox cache/transcoding |
| **Network** | 2.5GbE or 10GbE | If your internet supports it |
| **Power Supply** | 550W 80+ Platinum | Maximum efficiency for 24/7 |
| **Case** | Fractal Design Define 7 / SilverStone CS381 | 8+ drive bays, good cooling |

**Estimated Power Draw:** 45-90W idle, 150-250W under load

---

## Component Deep Dive

### CPU Requirements

**Minimum:**
- 2 cores / 4 threads
- x86_64 architecture (Intel or AMD)
- Supports hardware virtualization (for Docker/containers)

**Recommended:**
- 4+ cores / 8+ threads
- Intel Quick Sync or AMD VCE (for hardware transcoding)
- Low TDP (65W or less) for efficiency

**Why it matters:**
- Clawdbot: 1-2 cores typical usage
- Seedbox: 1-2 cores during active downloads
- Media Server: 1-4 cores per transcode (software) or minimal (hardware)

### RAM Requirements

**By Service:**
| Service | Minimum | Recommended | Heavy Use |
|---------|---------|-------------|-----------|
| Clawdbot | 1 GB | 2 GB | 4 GB |
| Seedbox (qBittorrent) | 512 MB | 1-2 GB | 4 GB+ |
| Media Server (Plex) | 1 GB | 2 GB | 4 GB+ |
| OS Overhead | 1-2 GB | 2 GB | 4 GB |
| **Total** | **4 GB** | **8 GB** | **16 GB** |

**RAM Tips:**
- DDR4 is fine; DDR5 not necessary
- ECC RAM not required (nice for ZFS though)
- Leave room for growth

### Storage Requirements

**SSD (Operating System + Applications):**
- 120 GB minimum
- 256 GB recommended (room for logs, temp files)
- NVMe preferred for faster boot times

**HDD (Media Storage):**
- Calculate: ~3-5 GB per hour of 1080p content
- 4K content: ~15-25 GB per hour
- Recommendation: Start with 4 TB, expand as needed

**Seedbox Storage:**
- Active downloads: 100-500 GB
- Seeding: Depends on ratio goals (1-4 TB typical)

**Configuration Options:**

```
Option A: Simple
├── 256 GB NVMe (OS + Apps + Clawdbot)
└── 4 TB HDD (Media + Seedbox)

Option B: Separate Cache
├── 256 GB NVMe (OS + Apps)
├── 1 TB NVMe (Seedbox cache + Transcoding)
└── 8 TB HDD (Media storage)

Option C: NAS/SAN
├── 256 GB NVMe (OS + Apps)
└── Network attached storage (Media + Seedbox)
```

### Network Requirements

**Internet:**
- Download: 50+ Mbps (media streaming)
- Upload: 20+ Mbps (seedbox sharing, Clawdbot webhooks)
- Unlimited data preferred

**Local Network:**
- Gigabit ethernet minimum
- Cat5e or Cat6 cables
- Gigabit router/switch

**Port Requirements:**
| Service | Ports | Direction |
|---------|-------|-----------|
| Clawdbot | 443, 80 | Inbound |
| SSH | 22 | Inbound (restricted) |
| Seedbox | 6881-6889 | Inbound/Outbound |
| Plex | 32400 | Inbound |
| Jellyfin | 8096 | Inbound |

---

## Software Stack Recommendations

### Operating System
**Ubuntu Server 22.04 LTS** (Recommended)
- Stable, long-term support
- Large community
- Easy package management

**Alternative: TrueNAS SCALE**
- Built-in ZFS
- Docker support
- Web-based management

### Clawdbot Setup
```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Clawdbot
sudo npm install -g clawdbot

# Configure auto-start
sudo systemctl enable clawdbot
```

### Seedbox Setup
**Recommended: qBittorrent + VPN**
```bash
# Install qBittorrent-nox (headless)
sudo apt install qbittorrent-nox

# Run as service
sudo systemctl enable qbittorrent-nox
```

**Docker Alternative:**
```yaml
version: '3'
services:
  qbittorrent:
    image: linuxserver/qbittorrent
    container_name: qbittorrent
    environment:
      - PUID=1000
      - PGID=1000
    volumes:
      - ./config:/config
      - /mnt/media/downloads:/downloads
    ports:
      - 8080:8080
      - 6881:6881
    restart: unless-stopped
```

### Media Server Setup
**Plex Media Server:**
```bash
# Download from plex.tv
wget https://downloads.plex.tv/plex-media-server-new/...
sudo dpkg -i plexmediaserver_*.deb
```

**Jellyfin (Open Source Alternative):**
```bash
# Install Jellyfin
curl -s https://repo.jellyfin.org/install-debuntu.sh | sudo bash
sudo apt install jellyfin
```

---

## Power & Cost Analysis

### Electricity Costs (24/7 Operation)

| Build | Power Draw | Monthly Cost* | Annual Cost |
|-------|-----------|---------------|-------------|
| Budget | 50W average | $4.50 | $54 |
| Recommended | 75W average | $6.75 | $81 |
| High-Performance | 120W average | $10.80 | $130 |

*Based on $0.12/kWh average North American rate

### VPS vs Local Comparison (3-year TCO)

| Cost | VPS ($20/mo) | Budget Local | Rec. Local | High-Perf Local |
|------|-------------|--------------|------------|-----------------|
| Hardware | $0 | $400 | $750 | $1500 |
| Electricity (3yr) | $0 | $162 | $243 | $390 |
| Internet | $0* | $0* | $0* | $0* |
| **3-Year Total** | **$720** | **$562** | **$993** | **$1890** |

*Assumes you already pay for internet

**Break-even point:** ~18 months for budget build, ~28 months for recommended build

---

## Buying Guide

### Where to Buy

**New Components:**
- Amazon (convenience, returns)
- Newegg (deals, bundles)
- Micro Center (in-store deals, especially CPUs)
- B&H Photo (no tax outside NY/NJ)

**Used/Refurbished (Great for budget builds):**
- eBay (corporate off-lease desktops)
- Facebook Marketplace (local deals)
- r/homelabsales (Reddit community)

**Recommended Pre-Built Options:**
- Dell OptiPlex 7050/7060 Micro (compact, quiet)
- HP EliteDesk 800 G3 Mini
- Lenovo ThinkCentre M720q

### Sample Shopping List (Recommended Build)

| Item | Model | Est. Price |
|------|-------|------------|
| CPU | Intel i5-12400 | $180 |
| Motherboard | B660 Micro-ATX | $100 |
| RAM | 16GB DDR4-3200 | $50 |
| SSD (OS) | 256GB NVMe | $40 |
| HDD (Media) | 4TB WD Blue | $80 |
| Case | Fractal Node 304 | $100 |
| PSU | 450W 80+ Gold | $70 |
| **Total** | | **~$620** |

---

## Setup Tips

### BIOS Settings
- Enable virtualization (VT-x/AMD-V) for Docker
- Set power profile to "Balanced" or "Power Saver"
- Disable unused features (audio if headless)

### OS Optimization
```bash
# Reduce swappiness for SSD longevity
sudo sysctl vm.swappiness=10

# Enable automatic updates for security
sudo apt install unattended-upgrades

# Monitor temperatures
sudo apt install lm-sensors
sudo sensors-detect
sensors
```

### Drive Management
```bash
# Check drive health
sudo smartctl -a /dev/sda

# Monitor disk usage
df -h

# Set up log rotation to prevent SSD wear
sudo nano /etc/logrotate.conf
```

### Network Optimization
```bash
# Increase TCP buffer sizes
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728

# Enable BBR congestion control
sudo nano /etc/sysctl.conf
# Add: net.ipv4.tcp_congestion_control=bbr
```

---

## Troubleshooting Common Issues

### High CPU Usage
- Check transcoding settings (use hardware acceleration)
- Limit concurrent seedbox connections
- Monitor with: `htop`, `iotop`

### High RAM Usage
- Add swap file if needed: `sudo fallocate -l 4G /swapfile`
- Limit Plex transcoder threads
- Check for memory leaks: `ps aux --sort=-%mem | head`

### Slow Network
- Test speed: `iperf3`, `speedtest-cli`
- Check cable quality
- Verify router QoS settings

### Storage Full
- Set up automated cleanup scripts
- Use `ncdu` to find large files
- Implement retention policies for seedbox

---

## Expansion Path

**When you need more:**

1. **More Storage:** Add external USB drives or NAS
2. **More RAM:** Easy upgrade on most motherboards
3. **Better Network:** Add 2.5GbE or 10GbE NIC
4. **Redundancy:** Add second machine for failover

---

## Quick Reference

### Minimum Viable Specs
- CPU: 4 threads
- RAM: 8 GB
- Storage: 120 GB SSD + 2 TB HDD
- Network: Gigabit ethernet

### Recommended Specs
- CPU: 6 cores + iGPU
- RAM: 16 GB
- Storage: 256 GB NVMe + 4 TB HDD
- Network: Gigabit ethernet, good upload speed

### Check Before Buying
- [ ] CPU supports Quick Sync / VCE?
- [ ] Motherboard has enough SATA ports?
- [ ] Case has room for all drives?
- [ ] Power supply sufficient wattage?
- [ ] Network card on motherboard?

---

*Generated for Simon Mills — February 2026*
