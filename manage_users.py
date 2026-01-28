#!/usr/bin/env python3
"""
User management script for Cloudways MCP Server
"""

import secrets
import sys
from auth.user_tokens import UserTokenManager

def generate_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def main():
    manager = UserTokenManager()
    
    if len(sys.argv) < 2:
        print("Cloudways MCP Server - User Management")
        print("=" * 50)
        print("\nUsage:")
        print("  python manage_users.py list                    - List all users")
        print("  python manage_users.py add <username> [email]  - Add a new user")
        print("  python manage_users.py remove <username>       - Remove a user")
        print("  python manage_users.py deactivate <username>   - Deactivate a user")
        print("  python manage_users.py activate <username>     - Activate a user")
        print("  python manage_users.py generate                - Generate a token")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        users = manager.list_users()
        if not users:
            print("No users configured.")
        else:
            print(f"\nConfigured Users ({len(users)}):")
            print("=" * 70)
            for user in users:
                status = "✓ Active" if user["active"] else "✗ Inactive"
                email = user.get("email", "N/A")
                role = user.get("role", "developer")
                print(f"  {status:12} | {user['username']:20} | {email:30} | {role}")
    
    elif command == "add":
        if len(sys.argv) < 3:
            print("Error: Username required")
            print("Usage: python manage_users.py add <username> [email]")
            sys.exit(1)
        
        username = sys.argv[2]
        email = sys.argv[3] if len(sys.argv) > 3 else None
        token = generate_token()
        
        if manager.add_user(username, token, email):
            print(f"\n✓ User '{username}' added successfully!")
            print(f"\nUser Token (save this - it won't be shown again):")
            print("=" * 70)
            print(f"{token}")
            print("=" * 70)
            print(f"\nUser's Cursor configuration:")
            print('{')
            print('  "mcpServers": {')
            print('    "Cloudways": {')
            print('      "command": "npx",')
            print('      "args": [')
            print('        "-y", "mcp-remote",')
            print('        "http://localhost:7001/mcp/mcp",')
            print(f'        "--header", "x-user-token: {token}"')
            print('      ]')
            print('    }')
            print('  }')
            print('}')
        else:
            print(f"✗ Failed to add user '{username}' (may already exist)")
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Error: Username required")
            print("Usage: python manage_users.py remove <username>")
            sys.exit(1)
        
        username = sys.argv[2]
        if manager.remove_user(username):
            print(f"✓ User '{username}' removed successfully")
        else:
            print(f"✗ User '{username}' not found")
    
    elif command == "deactivate":
        if len(sys.argv) < 3:
            print("Error: Username required")
            print("Usage: python manage_users.py deactivate <username>")
            sys.exit(1)
        
        username = sys.argv[2]
        if manager.deactivate_user(username):
            print(f"✓ User '{username}' deactivated (token no longer valid)")
        else:
            print(f"✗ User '{username}' not found")
    
    elif command == "activate":
        if len(sys.argv) < 3:
            print("Error: Username required")
            print("Usage: python manage_users.py activate <username>")
            sys.exit(1)
        
        username = sys.argv[2]
        if manager.activate_user(username):
            print(f"✓ User '{username}' activated (token now valid)")
        else:
            print(f"✗ User '{username}' not found")
    
    elif command == "generate":
        token = generate_token()
        print(f"\nGenerated Token:")
        print("=" * 70)
        print(f"{token}")
        print("=" * 70)
        print("\nUse this token with:")
        print('  python manage_users.py add <username> [email]')
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
