# ✅ Cloudways MCP Server - Deployment Complete!

**Deployment Date:** January 28, 2026  
**Status:** LIVE and HEALTHY  
**Server:** 159.203.171.11 (kmudghvkud)  
**Location:** `/home/master/applications/kmudghvkud/public_html/cloudways-mcp`  
**Port:** 8000  
**Target Domain:** https://cw-mcp.bmpweb.dev  

## Current Status

✅ **Server Running:** Process ID 357731  
✅ **Health Check:** `{"status":"healthy","redis":true,"initialized":true}`  
✅ **Redis Connected:** Pool size 500  
✅ **HTTP Client:** Pool size 500  
✅ **Token Auth:** Enabled  
✅ **User Created:** jonathan (it@bakemorepies.com)  

## Your Access Token

**Username:** jonathan  
**Token:** `89KSYZayhX_NHRWE2MQLtSEiTV4SSjXAlzJlVZ5y9Kw`  

**⚠️ SAVE THIS TOKEN - It won't be shown again!**

## Test Access (Internal Server)

```bash
# SSH into server
ssh -i ~/.ssh/cloudways_deploy_key master_xgawpdjexs@159.203.171.11

# Test health
curl http://localhost:8000/health

# View logs
tail -f /home/master/applications/kmudghvkud/public_html/cloudways-mcp/server.log

# Restart server
cd /home/master/applications/kmudghvkud/public_html/cloudways-mcp
./stop.sh
./start.sh
```

## Next Steps

### 1. Configure Domain & SSL

**Option A: Through Cloudways Panel (EASIEST)**

1. Go to Cloudways Dashboard
2. Navigate to your application (kmudghvkud)
3. Domain Management → Add Domain: `cw-mcp.bmpweb.dev`
4. SSL Certificate → Install Let's Encrypt for `cw-mcp.bmpweb.dev`
5. Application Settings → Configure reverse proxy to `localhost:8000`

**Option B: Manual Nginx Configuration**

Contact Cloudways support to add this to your nginx config:

```nginx
server {
    listen 80;
    listen 443 ssl;
    server_name cw-mcp.bmpweb.dev;

    ssl_certificate /path/to/cert;
    ssl_certificate_key /path/to/key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /mcp {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_set_header Cache-Control 'no-cache';
        proxy_set_header X-Accel-Buffering 'no';
        proxy_buffering off;
        chunked_transfer_encoding on;
        proxy_read_timeout 3600s;
    }
}
```

### 2. Set Up as System Service (Optional but Recommended)

**Create systemd service file:**

Contact Cloudways support to create `/etc/systemd/system/cloudways-mcp.service`:

```ini
[Unit]
Description=Cloudways MCP Server
After=network.target redis-server.service

[Service]
Type=simple
User=master_xgawpdjexs
WorkingDirectory=/home/master/applications/kmudghvkud/public_html/cloudways-mcp
Environment="PATH=/usr/bin:/home/master/.local/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/master/applications/kmudghvkud/public_html/cloudways-mcp/server.log
StandardError=append:/home/master/applications/kmudghvkud/public_html/cloudways-mcp/server.log

[Install]
WantedBy=multi-user.target
```

**Then:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudways-mcp
sudo systemctl start cloudways-mcp
sudo systemctl status cloudways-mcp
```

### 3. Update Your Cursor Configuration

**Your `~/.cursor/mcp.json` (Local Testing):**
```json
{
  "mcpServers": {
    "Cloudways": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://159.203.171.11:8000/mcp/mcp",
        "--header",
        "x-user-token: 89KSYZayhX_NHRWE2MQLtSEiTV4SSjXAlzJlVZ5y9Kw"
      ]
    }
  }
}
```

**After domain/SSL setup:**
```json
{
  "mcpServers": {
    "Cloudways": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://cw-mcp.bmpweb.dev/mcp/mcp",
        "--header",
        "x-user-token: 89KSYZayhX_NHRWE2MQLtSEiTV4SSjXAlzJlVZ5y9Kw"
      ]
    }
  }
}
```

### 4. Add Team Members

```bash
ssh -i ~/.ssh/cloudways_deploy_key master_xgawpdjexs@159.203.171.11

cd /home/master/applications/kmudghvkud/public_html/cloudways-mcp

# Add user
python3 manage_users.py add <username> <email>

# List users
python3 manage_users.py list

# Deactivate user
python3 manage_users.py deactivate <username>

# Remove user
python3 manage_users.py remove <username>
```

## Server Management Commands

```bash
# Connect to server
ssh -i ~/.ssh/cloudways_deploy_key master_xgawpdjexs@159.203.171.11

# Navigate to app
cd /home/master/applications/kmudghvkud/public_html/cloudways-mcp

# Start server
./start.sh

# Stop server
./stop.sh

# Restart server
./stop.sh && ./start.sh

# View logs (live)
tail -f server.log

# View last 100 lines
tail -100 server.log

# Check if running
ps aux | grep "python3 main.py"

# Test health
curl http://localhost:8000/health
```

## Update Procedure

```bash
cd /home/master/applications/kmudghvkud/public_html/cloudways-mcp

# Stop server
./stop.sh

# Pull latest code
git pull origin main

# Update dependencies (if requirements changed)
pip3 install --break-system-packages -r requirements.txt --upgrade

# Start server
./start.sh

# Verify
curl http://localhost:8000/health
```

## Troubleshooting

### Server Won't Start

```bash
# Check logs
cat server.log

# Check if port 8000 is in use
netstat -tulpn | grep 8000

# Kill any process on port 8000
lsof -ti:8000 | xargs kill -9

# Try starting again
./start.sh
```

### Can't Connect

```bash
# Test locally on server
curl http://localhost:8000/health

# Check if server is running
ps aux | grep "python3 main.py"

# Check logs for errors
tail -100 server.log
```

### Redis Issues

```bash
# Test Redis
redis-cli ping  # Should return PONG

# Restart Redis (if you have sudo)
sudo systemctl restart redis-server
```

## Current Configuration

**Environment File:** `/home/master/applications/kmudghvkud/public_html/cloudways-mcp/.env`
- Encryption Key: Set ✅
- Cloudways API: Configured ✅
- Redis: localhost:6379 ✅
- Port: 8000 ✅

**Security:**
- `.env` file permissions: 600 (owner read/write only)
- `users.json` not in git
- API keys server-side only
- User tokens required for access

## What's Working Right Now

✅ Server running on port 8000  
✅ Health endpoint responding  
✅ Redis connected  
✅ Token authentication enabled  
✅ You (jonathan) can connect  
✅ API credentials secured server-side  

## What's Not Yet Done

❌ Domain (cw-mcp.bmpweb.dev) not configured  
❌ SSL certificate not installed  
❌ Nginx reverse proxy not set up  
❌ Not running as systemd service (using nohup instead)  
❌ External access not tested  

## Testing the Deployment

### 1. Update Your Local Cursor Config

Edit `~/.cursor/mcp.json` with your token (shown above)

### 2. Reload MCP Servers

Press `Cmd+Shift+P` → "MCP: Reload MCP Servers"

### 3. Test Commands

Ask the AI:
- "List all Cloudways servers"
- "Show MySQL whitelisted IPs"
- "What's the disk usage on server 1488277?"

## Important Files

- **Logs:** `/home/master/applications/kmudghvkud/public_html/cloudways-mcp/server.log`
- **Config:** `/home/master/applications/kmudghvkud/public_html/cloudways-mcp/.env`
- **Users:** `/home/master/applications/kmudghvkud/public_html/cloudways-mcp/users.json`
- **PID:** `/home/master/applications/kmudghvkud/public_html/cloudways-mcp/server.pid`

## Support & Documentation

- **Quick Start:** `CLOUDWAYS-QUICKSTART.md`
- **Full Deployment:** `DEPLOY-TO-CLOUDWAYS.md`
- **GitHub:** https://github.com/BakeMorePies/cw-mcp
- **Email:** it@bakemorepies.com

---

**🎉 Congratulations! Your Cloudways MCP Server is live and ready to use!**

The server is currently accessible internally. Once you configure the domain and SSL, 
it will be available at `https://cw-mcp.bmpweb.dev` for your entire team.
