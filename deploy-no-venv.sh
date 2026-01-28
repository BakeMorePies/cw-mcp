#!/bin/bash
# Emergency deployment script for Cloudways without venv
# WARNING: This installs packages with --break-system-packages
# Only use if you cannot get sudo access to install python3.11-venv

set -e

echo "=========================================="
echo "Cloudways MCP - No-Venv Deployment"
echo "=========================================="
echo ""
echo "WARNING: This will install packages globally"
echo "Press Ctrl+C to cancel, Enter to continue..."
read

cd "$(dirname "$0")"

echo "Installing dependencies globally..."
pip3 install --break-system-packages -r requirements.txt

echo ""
echo "Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    
    # Generate encryption key
    ENCRYPTION_KEY=$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
    
    echo "ENCRYPTION_KEY=$ENCRYPTION_KEY" >> .env
    echo "CLOUDWAYS_EMAIL=it@bakemorepies.com" >> .env
    echo "CLOUDWAYS_API_KEY=Riz2UjjPJ7t65NiIWbNbJEJUq5SZDb" >> .env
    echo "CLOUDWAYS_SERVER_ID=1488277" >> .env
    echo "REDIS_URL=redis://localhost:6379/0" >> .env
    echo "PORT=8000" >> .env
    
    echo ".env file created"
else
    echo ".env file already exists"
fi

echo ""
echo "Creating users.json..."
if [ ! -f users.json ]; then
    cp users.json.example users.json
    echo "users.json created"
else
    echo "users.json already exists"
fi

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start the server: python3 main.py"
echo "2. Add users: python3 manage_users.py add <username> <email>"
echo "3. Configure nginx reverse proxy (see DEPLOY-TO-CLOUDWAYS.md)"
echo ""
