"""Rate limiting utilities for API endpoints."""

import time
from typing import Dict, Optional
from collections import defaultdict
from threading import Lock
from ..utils.logging import security_logger


class RateLimiter:
    """Simple in-memory rate limiter for API endpoints."""

    def __init__(self, requests: int = 100, window: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests: Number of requests allowed per window
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.requests_by_user: Dict[str, list] = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, user_id: str) -> bool:
        """
        Check if a request from the user is allowed.

        Args:
            user_id: ID of the user making the request

        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            current_time = time.time()
            # Remove old requests outside the time window
            self.requests_by_user[user_id] = [
                req_time for req_time in self.requests_by_user[user_id]
                if current_time - req_time < self.window
            ]

            # Check if user has exceeded the limit
            if len(self.requests_by_user[user_id]) >= self.requests:
                return False

            # Add current request to the list
            self.requests_by_user[user_id].append(current_time)
            return True

    def get_reset_time(self, user_id: str) -> Optional[float]:
        """
        Get the time when the rate limit will reset for the user.

        Args:
            user_id: ID of the user

        Returns:
            Reset time as Unix timestamp, or None if not rate limited
        """
        with self.lock:
            if user_id not in self.requests_by_user:
                return None

            if len(self.requests_by_user[user_id]) < self.requests:
                return None

            # Find the oldest request in the window
            oldest_request = min(self.requests_by_user[user_id])
            reset_time = oldest_request + self.window
            current_time = time.time()

            if current_time < reset_time:
                return reset_time
            else:
                return None


# Global rate limiter instance
rate_limiter = RateLimiter(requests=50, window=60)  # 50 requests per minute per user