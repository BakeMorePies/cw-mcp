#!/usr/bin/env python3
"""
Customer management for Cloudways MCP Server - BakeMorePies Edition
Token-based authentication for team members
"""

import json
import hashlib
import os
from datetime import datetime, timezone
from typing import Optional
import redis.asyncio as redis
from fastmcp import Context
from fastmcp.server.dependencies import get_http_request
import structlog

from config import fernet
from auth.user_tokens import UserTokenManager

logger = structlog.get_logger(__name__)

class Customer:
    def __init__(self, customer_id: str, email: str, cloudways_email: str, 
                 cloudways_api_key: str, username: str, created_at: datetime):
        self.customer_id = customer_id
        self.email = email
        self.cloudways_email = cloudways_email
        self.cloudways_api_key = cloudways_api_key
        self.username = username
        self.created_at = datetime.now(timezone.utc)
        self.last_seen = datetime.now(timezone.utc)

# Global token manager instance
token_manager = UserTokenManager()

async def get_customer_from_headers(ctx: Context, redis_client: Optional[redis.Redis] = None) -> Optional[Customer]:
    """
    Extract customer information from request headers.
    Uses token-based authentication for BakeMorePies team members.
    Cloudways credentials are read from server-side .env file only.
    """
    try:
        http_request = get_http_request()
        
        # Get user token from header
        user_token = http_request.headers.get("x-user-token")
        
        if not user_token:
            logger.warning("Missing user token in request")
            raise ValueError("Missing authentication: x-user-token header required")
        
        # Validate user token
        user = token_manager.validate_token(user_token)
        if not user:
            logger.warning("Invalid user token attempted")
            raise ValueError("Invalid authentication token")
        
        username = user.get("username")
        user_email = user.get("email", username)
        
        # Get server-side Cloudways credentials from environment
        cloudways_email = os.getenv("CLOUDWAYS_EMAIL")
        cloudways_api_key = os.getenv("CLOUDWAYS_API_KEY")
        
        if not cloudways_email or not cloudways_api_key:
            logger.error("Server misconfiguration: Cloudways credentials not set in .env")
            raise ValueError("Server configuration error: Contact administrator")
        
        # Get session identifier from MCP context or headers
        session_id = getattr(ctx, 'session_id', None) or http_request.headers.get('x-mcp-session-id')
        
        if not session_id:
            # Generate unique session ID for this connection
            import secrets
            session_id = secrets.token_urlsafe(32)
        
        # Create unique customer ID based on username and session
        # This ensures session isolation while allowing user identification
        customer_hash = hashlib.sha256(f"{username}:{session_id}".encode()).hexdigest()
        customer_id = f"user_{customer_hash[:16]}"
        
        # Check cache
        if redis_client:
            try:
                cached_data = await redis_client.get(f"customer:{customer_id}")
                if cached_data:
                    data = json.loads(cached_data)
                    decrypted_key = fernet.decrypt(data["encrypted_api_key"].encode()).decode()
                    
                    customer = Customer(
                        customer_id=customer_id,
                        email=data["email"],
                        cloudways_email=data["cloudways_email"],
                        cloudways_api_key=decrypted_key,
                        username=data["username"],
                        created_at=datetime.fromisoformat(data["created_at"])
                    )
                    logger.debug("User session loaded from cache", 
                               customer_id=customer_id, 
                               username=customer.username)
                    return customer
            except Exception as e:
                logger.warning("Failed to load session from cache", error=str(e))
        
        # Create new customer session
        customer = Customer(
            customer_id=customer_id,
            email=user_email,
            cloudways_email=cloudways_email,
            cloudways_api_key=cloudways_api_key,
            username=username,
            created_at=datetime.now(timezone.utc)
        )
        
        await _cache_customer(customer, redis_client)
        
        logger.info("New user session created", 
                   customer_id=customer_id, 
                   username=username,
                   user_email=user_email)
        
        # Log security event
        try:
            ip_address = getattr(http_request.client, 'host', 'unknown') if http_request.client else 'unknown'
            logger.info("User authenticated successfully",
                       username=username,
                       ip_address=ip_address,
                       customer_id=customer_id)
        except:
            pass
        
        return customer
        
    except ValueError as e:
        logger.error("Authentication failed", error=str(e))
        raise
    except Exception as e:
        logger.error("Failed to get customer from headers", error=str(e))
        return None

async def _cache_customer(customer: Customer, redis_client: Optional[redis.Redis] = None):
    """Cache customer data in Redis"""
    if not redis_client:
        return
    
    try:
        encrypted_api_key = fernet.encrypt(customer.cloudways_api_key.encode()).decode()
        customer_data = {
            "customer_id": customer.customer_id,
            "email": customer.email,
            "cloudways_email": customer.cloudways_email,
            "encrypted_api_key": encrypted_api_key,
            "username": customer.username,
            "created_at": customer.created_at.isoformat(),
            "last_seen": customer.last_seen.isoformat()
        }
        await redis_client.setex(f"customer:{customer.customer_id}", 3600, json.dumps(customer_data))
    except Exception as e:
        logger.error("Failed to cache customer", error=str(e))