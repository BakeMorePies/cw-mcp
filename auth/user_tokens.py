#!/usr/bin/env python3
"""
User token authentication for BakeMorePies Cloudways MCP Server
"""

import json
import os
from typing import Dict, Optional, List
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)

# Token storage file
TOKEN_FILE = Path(__file__).parent.parent / "users.json"

class UserTokenManager:
    """Manages user authentication tokens"""
    
    def __init__(self):
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Load users from JSON file"""
        if TOKEN_FILE.exists():
            try:
                with open(TOKEN_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error("Failed to load users file", error=str(e))
                return {"users": []}
        return {"users": []}
    
    def _save_users(self):
        """Save users to JSON file"""
        try:
            with open(TOKEN_FILE, 'w') as f:
                json.dump(self.users, f, indent=2)
            logger.info("Users file saved successfully")
        except Exception as e:
            logger.error("Failed to save users file", error=str(e))
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validate a user token
        
        Args:
            token: User's authentication token
            
        Returns:
            User information if valid, None otherwise
        """
        if not token:
            return None
        
        for user in self.users.get("users", []):
            if user.get("token") == token and user.get("active", True):
                logger.info("Token validated", username=user.get("username"))
                return user
        
        logger.warning("Invalid token attempted", token_prefix=token[:8] if len(token) > 8 else token)
        return None
    
    def add_user(self, username: str, token: str, email: str = None, role: str = "developer") -> bool:
        """
        Add a new user
        
        Args:
            username: User's name
            token: Authentication token
            email: User's email (optional)
            role: User's role (default: developer)
            
        Returns:
            True if user added successfully
        """
        # Check if user already exists
        for user in self.users.get("users", []):
            if user.get("username") == username:
                logger.warning("User already exists", username=username)
                return False
        
        # Add new user
        new_user = {
            "username": username,
            "token": token,
            "email": email,
            "role": role,
            "active": True
        }
        
        if "users" not in self.users:
            self.users["users"] = []
        
        self.users["users"].append(new_user)
        self._save_users()
        
        logger.info("User added successfully", username=username, role=role)
        return True
    
    def remove_user(self, username: str) -> bool:
        """Remove a user"""
        original_count = len(self.users.get("users", []))
        self.users["users"] = [u for u in self.users.get("users", []) if u.get("username") != username]
        
        if len(self.users["users"]) < original_count:
            self._save_users()
            logger.info("User removed", username=username)
            return True
        
        logger.warning("User not found", username=username)
        return False
    
    def deactivate_user(self, username: str) -> bool:
        """Deactivate a user without removing them"""
        for user in self.users.get("users", []):
            if user.get("username") == username:
                user["active"] = False
                self._save_users()
                logger.info("User deactivated", username=username)
                return True
        
        logger.warning("User not found", username=username)
        return False
    
    def activate_user(self, username: str) -> bool:
        """Activate a deactivated user"""
        for user in self.users.get("users", []):
            if user.get("username") == username:
                user["active"] = True
                self._save_users()
                logger.info("User activated", username=username)
                return True
        
        logger.warning("User not found", username=username)
        return False
    
    def list_users(self) -> List[Dict]:
        """List all users (without tokens)"""
        users = []
        for user in self.users.get("users", []):
            users.append({
                "username": user.get("username"),
                "email": user.get("email"),
                "role": user.get("role"),
                "active": user.get("active", True)
            })
        return users
    
    def get_user_by_token(self, token: str) -> Optional[str]:
        """Get username from token"""
        user = self.validate_token(token)
        return user.get("username") if user else None
