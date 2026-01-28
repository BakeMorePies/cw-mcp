# Cloudways MCP - Quick Start Guide

**URL:** `https://cw-mcp.bmpweb.dev`  
**Status:** ✅ LIVE

---

## For Team Members

### 1. Get Your Token
Contact it@bakemorepies.com for your personal access token

### 2. Configure Cursor
Edit `~/.cursor/mcp.json`:

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
        "x-user-token: [YOUR-TOKEN-HERE]"
      ]
    }
  }
}
```

### 3. Reload & Test
1. `Cmd+Shift+P` → "MCP: Reload MCP Servers"
2. Ask AI: "List all Cloudways servers"

---

## For Server Operators

### Connect
```bash
ssh -i ~/.ssh/cloudways_deploy_key master_xgawpdjexs@159.203.171.11
cd /home/master/applications/kmudghvkud/public_html/cloudways-mcp
```

### Common Commands
```bash
PM2=/home/master/bin/npm/lib/node_modules/bin/pm2

# Monitor
$PM2 list
$PM2 logs cloudways-mcp
$PM2 monit

# Manage
$PM2 restart cloudways-mcp
$PM2 stop cloudways-mcp
$PM2 start cloudways-mcp

# Health check
curl http://localhost:8000/health
curl https://cw-mcp.bmpweb.dev/health
```

### User Management
```bash
python3 manage_users.py add <username> <email>
python3 manage_users.py list
python3 manage_users.py deactivate <username>
python3 manage_users.py remove <username>
```

### Update Code
```bash
git pull origin main
pip3 install --break-system-packages -r requirements.txt --upgrade
$PM2 restart cloudways-mcp
```

---

## Available MCP Tools

Once connected, you can ask the AI to:
- List Cloudways servers
- Show MySQL whitelisted IPs
- Get server disk usage
- List applications
- View database credentials
- Manage server resources
- Check application status
- **...and 36 more operations!**

---

## Troubleshooting

**Can't connect?**
- Check token is correct
- Reload MCP servers in Cursor
- Test: `curl https://cw-mcp.bmpweb.dev/health`

**Server down?**
- SSH in and run: `$PM2 list`
- If stopped: `$PM2 start cloudways-mcp`
- Check logs: `$PM2 logs cloudways-mcp --err`

**Need help?**
- Email: it@bakemorepies.com
- Docs: See PRODUCTION-READY.md
- GitHub: https://github.com/BakeMorePies/cw-mcp

---

**Made with 🍕 by BakeMorePies**
