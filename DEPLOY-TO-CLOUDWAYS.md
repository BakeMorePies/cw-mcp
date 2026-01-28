# Deploying Cloudways MCP to Cloudways Server

This guide covers deploying the BakeMorePies Cloudways MCP Server to your Cloudways hosting.

## Prerequisites

- Cloudways server (Server ID: 1488277)
- Application directory: `kmudghvkud`
- SSH access to the server
- Python 3.11+ installed on server
- Redis installed on server

## Deployment Steps

### 1. Connect to Your Cloudways Server

```bash
# SSH into your Cloudways server
ssh master@[your-server-ip] -i [your-ssh-key]
```

### 2. Navigate to Application Directory

```bash
cd /home/master/applications/kmudghvkud
```

### 3. Clone the Repository

```bash
git clone https://github.com/BakeMorePies/cw-mcp.git
cd cw-mcp
```

### 4. Set Up Python Environment

```bash
# Install Python 3.11+ if not available
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Required .env configuration:**
```bash
# Generate encryption key
ENCRYPTION_KEY=$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')

# Cloudways API credentials
CLOUDWAYS_EMAIL=it@bakemorepies.com
CLOUDWAYS_API_KEY=Riz2UjjPJ7t65NiIWbNbJEJUq5SZDb
CLOUDWAYS_SERVER_ID=1488277

# Redis configuration
REDIS_URL=redis://localhost:6379/0

# Server configuration
PORT=8000  # Or any available port
WORKERS=1
```

### 6. Install and Configure Redis

```bash
# Install Redis
sudo apt install redis-server -y

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping  # Should return PONG
```

### 7. Create Systemd Service

Create a systemd service file for automatic startup:

```bash
sudo nano /etc/systemd/system/cloudways-mcp.service
```

**Service file content:**
```ini
[Unit]
Description=Cloudways MCP Server
After=network.target redis-server.service

[Service]
Type=simple
User=master
WorkingDirectory=/home/master/applications/kmudghvkud/cw-mcp
Environment="PATH=/home/master/applications/kmudghvkud/cw-mcp/venv/bin"
ExecStart=/home/master/applications/kmudghvkud/cw-mcp/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start the service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudways-mcp
sudo systemctl start cloudways-mcp

# Check status
sudo systemctl status cloudways-mcp
```

### 8. Configure Nginx Reverse Proxy

Create nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/cloudways-mcp
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name cloudways-mcp.bakemorepies.com;  # Change to your domain

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

    # MCP endpoint with SSE support
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

**Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/cloudways-mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 9. Install SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d cloudways-mcp.bakemorepies.com
```

### 10. Add Team Members

```bash
cd /home/master/applications/kmudghvkud/cw-mcp
source venv/bin/activate

# Add users
python manage_users.py add jonathan it@bakemorepies.com
python manage_users.py add [username] [email]

# List users
python manage_users.py list
```

### 11. Test the Deployment

```bash
# Test health endpoint
curl https://cloudways-mcp.bakemorepies.com/health

# Expected response:
# {"status":"healthy","redis":true,"initialized":true}
```

## Team Member Configuration

After deployment, team members update their `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "Cloudways": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://cloudways-mcp.bakemorepies.com/mcp/mcp",
        "--header",
        "x-user-token: [their-token]"
      ]
    }
  }
}
```

## Maintenance

### View Logs

```bash
# Service logs
sudo journalctl -u cloudways-mcp -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Service

```bash
sudo systemctl restart cloudways-mcp
```

### Update Server

```bash
cd /home/master/applications/kmudghvkud/cw-mcp
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart cloudways-mcp
```

### Manage Users

```bash
cd /home/master/applications/kmudghvkud/cw-mcp
source venv/bin/activate

# Add user
python manage_users.py add <username> <email>

# List users
python manage_users.py list

# Deactivate user
python manage_users.py deactivate <username>

# Remove user
python manage_users.py remove <username>
```

## Security Considerations

1. **.env file protection:**
   ```bash
   chmod 600 .env
   ```

2. **Firewall configuration:**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **IP whitelist (optional):**
   Add this to nginx configuration to restrict access:
   ```nginx
   allow 1.2.3.4;  # Your office IP
   deny all;
   ```

4. **Regular updates:**
   ```bash
   # Set up automatic security updates
   sudo apt install unattended-upgrades -y
   ```

## Troubleshooting

### Server Won't Start

```bash
# Check logs
sudo journalctl -u cloudways-mcp -n 50

# Check if port is in use
sudo lsof -i :8000

# Test Redis
redis-cli ping
```

### Nginx Errors

```bash
# Test nginx configuration
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Can't Connect from Cursor

1. **Check firewall:** Ensure ports 80/443 are open
2. **Check SSL:** Verify certificate is valid
3. **Test endpoint:** `curl https://cloudways-mcp.bakemorepies.com/health`
4. **Check token:** Verify user token is valid

## Backup and Recovery

### Backup users.json

```bash
# Backup user database
cp /home/master/applications/kmudghvkud/cw-mcp/users.json ~/users.json.backup

# Automated backup (add to crontab)
0 0 * * * cp /home/master/applications/kmudghvkud/cw-mcp/users.json ~/backups/users-$(date +\%Y\%m\%d).json
```

### Recovery

```bash
# Restore users
cp ~/users.json.backup /home/master/applications/kmudghvkud/cw-mcp/users.json
sudo systemctl restart cloudways-mcp
```

## Performance Tuning

### For High Traffic

1. **Increase Redis connection pool:**
   ```bash
   # In .env
   REDIS_POOL_SIZE=1000
   HTTP_POOL_SIZE=1000
   ```

2. **Add multiple workers (if needed):**
   ```bash
   # In .env
   WORKERS=2  # Be careful with session state
   ```

3. **Enable Redis persistence:**
   ```bash
   # Edit /etc/redis/redis.conf
   save 900 1
   save 300 10
   save 60 10000
   ```

## Support

**Issues?**
- Check GitHub Issues: https://github.com/BakeMorePies/cw-mcp/issues
- Contact: it@bakemorepies.com
- Server logs: `sudo journalctl -u cloudways-mcp -f`
