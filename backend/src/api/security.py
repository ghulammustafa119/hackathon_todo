"""
Security middleware and utilities for FastAPI.
- Rate limiting for auth endpoints (IP-based)
- Security response headers
"""

import time
import logging
from collections import defaultdict
from threading import Lock
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# --- IP-based rate limiter for auth endpoints ---

class AuthRateLimiter:
    """
    Simple in-memory rate limiter keyed by client IP.
    Used to prevent brute-force login/register attempts.
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str) -> bool:
        """Return True if allowed, False if rate-limited."""
        now = time.time()
        with self._lock:
            # Prune expired entries
            self._hits[key] = [t for t in self._hits[key] if now - t < self.window]
            if len(self._hits[key]) >= self.max_requests:
                return False
            self._hits[key].append(now)
            return True

    def remaining(self, key: str) -> int:
        now = time.time()
        with self._lock:
            self._hits[key] = [t for t in self._hits[key] if now - t < self.window]
            return max(0, self.max_requests - len(self._hits[key]))


# Global auth rate limiter: 10 attempts per minute per IP
auth_limiter = AuthRateLimiter(max_requests=10, window_seconds=60)


def get_client_ip(request: Request) -> str:
    """Extract client IP, respecting X-Forwarded-For from proxies."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_auth_rate_limit(request: Request) -> None:
    """
    Call this as a dependency on auth endpoints.
    Raises 429 if the client IP is rate-limited.
    """
    ip = get_client_ip(request)
    if not auth_limiter.check(ip):
        logger.warning(f"Rate limit exceeded for IP {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Please try again later.",
            headers={"Retry-After": str(auth_limiter.window)},
        )


# --- Security headers middleware ---

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add standard security headers to every response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
