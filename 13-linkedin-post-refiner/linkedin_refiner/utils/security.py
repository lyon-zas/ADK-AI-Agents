"""
Security Utilities for LinkedIn Post Refiner

This module provides security functions for PII protection,
API key handling, and rate limiting.
"""

import os
import re
from datetime import datetime, timedelta
from typing import Dict, Optional


# PII Patterns for redaction
PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone_us": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    "phone_intl": r"\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
}


def redact_pii(text: str) -> str:
    """
    Redact personally identifiable information from text.
    
    Use this before logging or telemetry to protect user privacy.
    
    Args:
        text: Input text that may contain PII
        
    Returns:
        Text with PII patterns replaced with [REDACTED_TYPE]
    """
    result = text
    for pii_type, pattern in PII_PATTERNS.items():
        result = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", result)
    return result


def get_api_key(key_name: str = "GOOGLE_API_KEY") -> str:
    """
    Securely retrieve API key from environment variables.
    
    Args:
        key_name: Name of the environment variable
        
    Returns:
        API key string
        
    Raises:
        EnvironmentError: If key is not configured
    """
    key = os.environ.get(key_name)
    if not key:
        raise EnvironmentError(
            f"{key_name} not configured. Set it in your environment or .env file."
        )
    return key


def mask_api_key(key: str, visible_chars: int = 4) -> str:
    """
    Mask an API key for safe logging.
    
    Args:
        key: Full API key
        visible_chars: Number of characters to show at end
        
    Returns:
        Masked key like "***...xy4z"
    """
    if len(key) <= visible_chars:
        return "*" * len(key)
    return "*" * (len(key) - visible_chars) + key[-visible_chars:]


class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    For production, use Redis-based distributed rate limiting.
    
    Attributes:
        max_requests: Maximum requests allowed in the window
        window_seconds: Time window in seconds
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 3600):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per window (default: 10/hour)
            window_seconds: Window duration in seconds (default: 1 hour)
        """
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, user_id: str) -> bool:
        """
        Check if a request from user_id is allowed.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if request is allowed, False if rate limited
        """
        now = datetime.utcnow()
        user_requests = self.requests.get(user_id, [])
        
        # Remove expired requests
        user_requests = [t for t in user_requests if now - t < self.window]
        
        if len(user_requests) >= self.max_requests:
            return False
        
        user_requests.append(now)
        self.requests[user_id] = user_requests
        return True
    
    def get_remaining(self, user_id: str) -> int:
        """
        Get remaining requests for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Number of remaining requests in current window
        """
        now = datetime.utcnow()
        user_requests = self.requests.get(user_id, [])
        active_requests = [t for t in user_requests if now - t < self.window]
        return max(0, self.max_requests - len(active_requests))
    
    def reset(self, user_id: Optional[str] = None) -> None:
        """
        Reset rate limit counters.
        
        Args:
            user_id: If provided, reset only this user. Otherwise reset all.
        """
        if user_id:
            self.requests.pop(user_id, None)
        else:
            self.requests.clear()


# Default rate limiter instance: 10 refinements per hour
default_rate_limiter = RateLimiter(max_requests=10, window_seconds=3600)


def check_rate_limit(user_id: str) -> dict:
    """
    Check rate limit for a user using the default limiter.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        Dict with allowed status and remaining requests
    """
    allowed = default_rate_limiter.is_allowed(user_id)
    remaining = default_rate_limiter.get_remaining(user_id)
    
    return {
        "allowed": allowed,
        "remaining": remaining,
        "limit": default_rate_limiter.max_requests,
        "window_seconds": default_rate_limiter.window.total_seconds()
    }
