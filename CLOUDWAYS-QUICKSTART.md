# Cloudways MCP - Quick Deployment Guide

**Target URL:** `https://cw-mcp.bmpweb.dev`  
**Server:** 159.203.171.11 (kmudghvkud)  
**Current Status:** Repository cloned, needs package installation  

## Current Situation

✅ Repository cloned to: `/home/master/applications/kmudghvkud/public_html/cloudways-mcp`  
✅ Python 3.11.2 available  
✅ Redis running  
❌ **BLOCKED:** Cannot create virtual environment (needs `python3.11-venv` package)  

## Two Deployment Options

### Option 1: Request Venv Support (RECOMMENDED)

**Contact Cloudways Support:**

*"Hi, I need `python3.11-venv` installed on my server (159.203.171.11 - kmudghvkud). 
I'm deploying a Python application that requires virtual environments. Can you please run:
`sudo apt install python3.11-venv python3-pip`"*

**Then deploy normally:**
```bash
ssh -i ~/.ssh/cloudways_deploy_key master_xgawpdjexs@159.203.171.11

cd /home/master/applications/kmudghvkud/public_html/cloudways-mcp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings
nano .env

# Add encryption key
python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
# Copy the output to ENCRYPTION_KEY in .env

# Run server
python main.py
```

### Option 2: Deploy Without Venv (WORKAROUND)

**Use if you can't get sudo access:**

```bash
ssh -i ~/.ssh/cloudways_deploy_key master_xgawpdjexs@159.203.171.11

cd /home/master/applications/kmudghvkud/public_html/cloudways-mcp

# Run deployment script
chmod +x deploy-no-venv.sh
./deploy-no-venv.sh

# Start server
python3 main.py
```

**⚠️ WARNING:** This installs packages globally with `--break-system-packages`. 
Not ideal but works if venv isn't available.

## After Installation

### 1. Configure as a Service

Create systemd service (requires sudo or Cloudways support):

```bash
sudo nano /etc/systemd/system/cloudways-mcp.service
```

```ini
[Unit]
Description=Cloudways MCP Server
After=network.target redis-server.service

[Service]
Type=simple
User=master_xgawpdjexs
WorkingDirectory=/home/master/applications/kmudghvkud/public_html/cloudways-mcp
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudways-mcp
sudo systemctl start cloudways-mcp
sudo systemctl status cloudways-mcp
```

### 2. Configure Domain in Cloudways Panel

1. **Go to Cloudways Panel** → Your Application (kmudghvkud)
2. **Domain Management** → Add Domain: `cw-mcp.bmpweb.dev`
3. **SSL Certificate** → Install Let's Encrypt for `cw-mcp.bmpweb.dev`

### 3. Configure Nginx Reverse Proxy

The application runs on port 8000, so we need nginx to proxy requests:

**Check current nginx config location:**
```bash
ls -la /etc/nginx/sites-available/
```

**For Cloudways, the config might be at:**
```bash
/home/master/applications/kmudghvkud/conf/nginx/nginx.conf
```

**Add this location block:**
```nginx
location /mcp-api/ {
    proxy_pass http://localhost:8000/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # SSE support for MCP
    proxy_buffering off;
    proxy_set_header Cache-Control 'no-cache';
    proxy_set_header X-Accel-Buffering 'no';
    chunked_transfer_encoding on;
    proxy_read_timeout 3600s;
}
```

**Or create a subdomain application in Cloudways:**
1. Create new application "cloudways-mcp"
2. Point domain `cw-mcp.bmpweb.dev` to it
3. Set up reverse proxy to `localhost:8000`

### 4. Add Team Members

```bash
cd /home/master/applications/kmudghvkud/public_html/cloudways-mcp
python3 manage_users.py add jonathan it@bakemorepies.com
# Save the token!
```

### 5. Test Deployment

```bash
# From server
curl http://localhost:8000/health

# From external
curl https://cw-mcp.bmpweb.dev/health

# Expected:
# {"status":"healthy","redis":true,"initialized":true}
```

## Team Member Configuration

Once deployed, team members use:

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
        "x-user-token: [their-token-here]"
      ]
    }
  }
}
```

## Troubleshooting

### Server Won't Start

**Check logs:**
```bash
# If using systemd
sudo journalctl -u cloudways-mcp -f

# If running directly
python3 main.py --dev  # See error output
```

**Common issues:**
- **Port 8000 in use:** Change `PORT=8001` in `.env`
- **Redis not running:** Check `redis-cli ping`
- **Missing .env:** Copy from `.env.example` and configure
- **Import errors:** Install dependencies again

### Cannot Connect from Cursor

1. **Test locally on server:** `curl http://localhost:8000/health`
2. **Test externally:** `curl https://cw-mcp.bmpweb.dev/health`
3. **Check nginx:** Verify reverse proxy configuration
4. **Check firewall:** Ensure port 80/443 open
5. **Check SSL:** Verify certificate is valid

### Need Sudo Access?

Some tasks require sudo (systemd service, nginx config, venv install).

**Options:**
1. **Cloudways Support:** They can run sudo commands for you
2. **Master User:** If you have master user access
3. **Application Panel:** Some configs can be done through Cloudways panel

## Manual Testing

```bash
# SSH into server
ssh -i ~/.ssh/cloudways_deploy_key master_xgawpdjexs@159.203.171.11

# Navigate to app
cd /home/master/applications/kmudghvkud/public_html/cloudways-mcp

# Test locally
python3 main.py --dev

# In another terminal, test:
curl http://localhost:8000/health
```

## Maintenance

### View Logs
```bash
tail -f /var/log/cloudways-mcp.log  # If configured
sudo journalctl -u cloudways-mcp -f  # If using systemd
```

### Restart Server
```bash
sudo systemctl restart cloudways-mcp  # If using systemd
# Or kill and restart manually
```

### Update Code
```bash
cd /home/master/applications/kmudghvkud/public_html/cloudways-mcp
git pull origin main
# Reinstall if requirements changed
pip install -r requirements.txt --upgrade
sudo systemctl restart cloudways-mcp
```

## Security Checklist

- [ ] `.env` file has restricted permissions (600)
- [ ] `users.json` is not in git (check `.gitignore`)
- [ ] SSL certificate installed for `cw-mcp.bmpweb.dev`
- [ ] Firewall allows only necessary ports (80, 443)
- [ ] Redis is not exposed to external network
- [ ] User tokens are unique and secure
- [ ] Server logs are monitored

## Quick Commands Reference

```bash
# Connect to server
ssh -i ~/.ssh/cloudways_deploy_key master_xgawpdjexs@159.203.171.11

# Go to app directory
cd /home/master/applications/kmudghvkud/public_html/cloudways-mcp

# Add user
python3 manage_users.py add <username> <email>

# List users
python3 manage_users.py list

# Test health
curl http://localhost:8000/health

# Start server manually
python3 main.py

# View service status
sudo systemctl status cloudways-mcp
```

## Support

**Need help?**
- Email: it@bakemorepies.com
- GitHub: https://github.com/BakeMorePies/cw-mcp
- Cloudways Support: For sudo access requests

---

**Current Deployment Status:** Repository cloned, awaiting venv support or using no-venv workaround
